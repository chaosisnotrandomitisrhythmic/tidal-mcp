#!/usr/bin/env python3
"""
TIDAL MCP Server - Simplified Architecture
Clean, minimal implementation with direct TIDAL API integration
"""

import webbrowser
from pathlib import Path
from typing import List

import anyio
import tidalapi
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Import all models from the separate models module
from .models import (
    Track,
    TrackList,
    Playlist,
    PlaylistList,
    PlaylistTracks,
    CreatePlaylistResult,
    AddTracksResult,
    AuthResult,
)


# Server configuration
SERVER_NAME = "TIDAL MCP"
SERVER_INSTRUCTIONS = """MCP server for TIDAL music streaming service integration. 

Provides tools for searching music, managing playlists, and accessing your TIDAL library.

Authentication:
- Use the 'login' tool first to authenticate with TIDAL via OAuth
- Session is persisted and reused across restarts

Search:
- Use 'search_tracks' to find music (works best with artist names or song titles)

Playlist Management:
- Create playlists with 'create_playlist'
- Add tracks with 'add_tracks_to_playlist'
- List your playlists with 'get_user_playlists'
- Get playlist tracks with 'get_playlist_tracks'

Library Access:
- Get favorite tracks with 'get_favorites'
"""

# Initialize MCP server with metadata
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=SERVER_INSTRUCTIONS,
)

# Session management - use project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Navigate up to project root
SESSION_DIR = PROJECT_ROOT / ".tidal-sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = SESSION_DIR / "session.json"
session = tidalapi.Session()


async def ensure_authenticated() -> bool:
    """Check if user is authenticated with TIDAL"""
    if await anyio.Path(SESSION_FILE).exists():
        await anyio.to_thread.run_sync(session.load_session_from_file, SESSION_FILE)
    return await anyio.to_thread.run_sync(session.check_login)


@mcp.tool(
    annotations={
        "title": "Authenticate with TIDAL",
        "readOnlyHint": False,
        "openWorldHint": True,
        "idempotentHint": False,
    }
)
async def login() -> AuthResult:
    """
    Authenticate with TIDAL using OAuth browser flow.
    Opens browser automatically for secure login.

    Returns:
        Authentication status and user information
    """
    # Check if already authenticated
    if await ensure_authenticated():
        return AuthResult(
            status="success",
            message="Already authenticated with TIDAL",
            authenticated=True,
        )

    try:
        # Start OAuth flow in thread to avoid blocking
        login_obj, future = await anyio.to_thread.run_sync(session.login_oauth)

        # Open browser for authentication
        auth_url = login_obj.verification_uri_complete
        if not auth_url.startswith("http"):
            auth_url = "https://" + auth_url

        # Browser will open automatically
        await anyio.to_thread.run_sync(webbrowser.open, auth_url)

        # Wait for completion
        await anyio.to_thread.run_sync(future.result)

        # Verify and save session
        if await anyio.to_thread.run_sync(session.check_login):
            await anyio.to_thread.run_sync(session.save_session_to_file, SESSION_FILE)
            return AuthResult(
                status="success",
                message="Successfully authenticated with TIDAL",
                authenticated=True,
            )
        else:
            raise ToolError("Authentication failed - OAuth flow did not complete")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Authentication error: {str(e)}")


@mcp.tool()
async def search_tracks(query: str, limit: int = 10) -> TrackList:
    """
    Search for tracks on TIDAL.

    Args:
        query: Search query - works best with artist name, song title, or "Artist Song"
        limit: Maximum number of results (default: 10, max: 50)

    Returns:
        List of tracks with id, title, artist, album, and duration
    """
    if not ensure_authenticated():
        raise ToolError("Not authenticated. Please run the 'login' tool first.")

    try:
        # Perform search
        limit = min(max(1, limit), 50)  # Ensure limit is between 1-50
        results = session.search(query, models=[tidalapi.Track], limit=limit)

        # Format results
        tracks = []
        for track in results.get("tracks", []):
            tracks.append(
                Track(
                    id=str(track.id),
                    title=track.name,
                    artist=track.artist.name if track.artist else "Unknown Artist",
                    album=track.album.name if track.album else "Unknown Album",
                    duration_seconds=track.duration,
                    url=f"https://tidal.com/browse/track/{track.id}",
                )
            )

        return TrackList(
            status="success", query=query, count=len(tracks), tracks=tracks
        )
    except Exception as e:
        raise ToolError(f"Search failed: {str(e)}")


@mcp.tool()
def get_favorites(limit: int = 20) -> TrackList:
    """
    Get user's favorite tracks from TIDAL.

    Args:
        limit: Maximum number of tracks to retrieve (default: 20)

    Returns:
        List of favorite tracks
    """
    if not ensure_authenticated():
        raise ToolError("Not authenticated. Please run the 'login' tool first.")

    try:
        favorites = session.user.favorites.tracks(limit=limit)

        tracks = []
        for track in favorites:
            tracks.append(
                Track(
                    id=str(track.id),
                    title=track.name,
                    artist=track.artist.name if track.artist else "Unknown Artist",
                    album=track.album.name if track.album else "Unknown Album",
                    duration_seconds=track.duration,
                    url=f"https://tidal.com/browse/track/{track.id}",
                )
            )

        return TrackList(status="success", count=len(tracks), tracks=tracks)
    except Exception as e:
        raise ToolError(f"Failed to get favorites: {str(e)}")


@mcp.tool()
def create_playlist(
    name: str, description: str = ""
) -> CreatePlaylistResult:
    """
    Create a new playlist in your TIDAL account.

    Args:
        name: Name of the playlist
        description: Optional description for the playlist

    Returns:
        Created playlist information including ID and URL
    """
    if not ensure_authenticated():
        raise ToolError("Not authenticated. Please run the 'login' tool first.")

    try:
        # Create playlist
        playlist = session.user.create_playlist(name, description)

        return CreatePlaylistResult(
            status="success",
            playlist=Playlist(
                id=str(playlist.id),
                name=playlist.name,
                description=playlist.description or "",
                track_count=0,
                url=f"https://tidal.com/browse/playlist/{playlist.id}",
            ),
            message=f"Created playlist '{name}'",
        )
    except Exception as e:
        raise ToolError(f"Failed to create playlist: {str(e)}")


@mcp.tool()
def add_tracks_to_playlist(
    playlist_id: str, track_ids: List[str]
) -> AddTracksResult:
    """
    Add tracks to an existing playlist.

    Args:
        playlist_id: ID of the playlist to add tracks to
        track_ids: List of track IDs to add (from search results)

    Returns:
        Success status and number of tracks added
    """
    if not ensure_authenticated():
        raise ToolError("Not authenticated. Please run the 'login' tool first.")

    try:
        # Get the playlist
        playlist = session.playlist(playlist_id)
        if not playlist:
            raise ToolError(f"Playlist with ID '{playlist_id}' not found")

        # Convert track IDs to integers (TIDAL API expects integers)
        track_ids_int = [int(track_id) for track_id in track_ids]

        # Add tracks to playlist
        success = playlist.add(track_ids_int)

        if success:
            return AddTracksResult(
                status="success",
                message=f"Added {len(track_ids)} tracks to playlist '{playlist.name}'",
                playlist_id=playlist_id,
                playlist_name=playlist.name,
                tracks_added=len(track_ids),
                playlist_url=f"https://tidal.com/browse/playlist/{playlist_id}",
            )
        else:
            raise ToolError("Failed to add tracks to playlist")
    except ValueError as e:
        raise ToolError(f"Invalid track ID format: {str(e)}")
    except Exception as e:
        raise ToolError(f"Failed to add tracks: {str(e)}")


@mcp.tool()
def get_user_playlists(limit: int = 20) -> PlaylistList:
    """
    Get list of user's playlists from TIDAL.

    Args:
        limit: Maximum number of playlists to return (default: 20)

    Returns:
        List of user's playlists with ID, name, description, and track count
    """
    if not ensure_authenticated():
        raise ToolError("Not authenticated. Please run the 'login' tool first.")

    try:
        # Get all playlists (API doesn't support limit parameter)
        all_playlists = session.user.playlists()
        
        # Apply client-side limiting
        limited_playlists = all_playlists[:limit] if limit else all_playlists

        playlist_list = []
        for playlist in limited_playlists:
            playlist_list.append(
                Playlist(
                    id=str(playlist.id),
                    name=playlist.name,
                    description=playlist.description or "",
                    track_count=getattr(playlist, "num_tracks", 0),
                    url=f"https://tidal.com/browse/playlist/{playlist.id}",
                )
            )

        return PlaylistList(
            status="success", count=len(playlist_list), playlists=playlist_list
        )
    except Exception as e:
        raise ToolError(f"Failed to get playlists: {str(e)}")


@mcp.tool()
async def get_playlist_tracks(
    playlist_id: str, limit: int = 100
) -> PlaylistTracks:
    """
    Get tracks from a specific playlist.

    Args:
        playlist_id: ID of the playlist
        limit: Maximum number of tracks to return (default: 100)

    Returns:
        List of tracks in the playlist
    """
    if not await ensure_authenticated():
        raise ToolError("Not authenticated. Please run the 'login' tool first.")

    try:
        playlist = await anyio.to_thread.run_sync(session.playlist, playlist_id)
        if not playlist:
            raise ToolError(f"Playlist with ID '{playlist_id}' not found")

        # Get tracks from playlist in thread pool
        playlist_tracks = await anyio.to_thread.run_sync(playlist.tracks, limit=limit)

        tracks = []
        for track in playlist_tracks:
            tracks.append(
                Track(
                    id=str(track.id),
                    title=track.name,
                    artist=track.artist.name if track.artist else "Unknown Artist",
                    album=track.album.name if track.album else "Unknown Album",
                    duration_seconds=track.duration,
                    url=f"https://tidal.com/browse/track/{track.id}",
                )
            )

        return PlaylistTracks(
            status="success",
            playlist_name=playlist.name,
            playlist_id=playlist_id,
            count=len(tracks),
            tracks=tracks,
        )
    except Exception as e:
        raise ToolError(f"Failed to get playlist tracks: {str(e)}")


def run_server() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run_server()
