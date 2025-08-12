#!/usr/bin/env python3
"""
TIDAL MCP Server - Simplified Architecture
Clean, minimal implementation with direct TIDAL API integration
"""

import webbrowser
from pathlib import Path
from typing import List

import tidalapi
from mcp.server.fastmcp import FastMCP

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
    ErrorResult,
)


# Initialize MCP server with metadata
mcp = FastMCP(
    name="TIDAL MCP",
    instructions="MCP server for TIDAL music streaming service integration. Provides tools for searching music, managing playlists, and accessing your TIDAL library.",
)

# Session management - use project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Navigate up to project root
SESSION_DIR = PROJECT_ROOT / ".tidal-sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = SESSION_DIR / "session.json"
session = tidalapi.Session()


def ensure_authenticated() -> bool:
    """Check if user is authenticated with TIDAL"""
    if SESSION_FILE.exists():
        session.load_session_from_file(SESSION_FILE)
    return session.check_login()


@mcp.tool()
def login() -> AuthResult:
    """
    Authenticate with TIDAL using OAuth browser flow.
    Opens browser automatically for secure login.

    Returns:
        Authentication status and user information
    """
    # Check if already authenticated
    if ensure_authenticated():
        return AuthResult(
            status="success",
            message="Already authenticated with TIDAL",
            authenticated=True,
        )

    try:
        # Start OAuth flow
        login_obj, future = session.login_oauth()

        # Open browser for authentication
        auth_url = login_obj.verification_uri_complete
        if not auth_url.startswith("http"):
            auth_url = "https://" + auth_url

        # Browser will open automatically
        webbrowser.open(auth_url)

        # Wait for completion
        future.result()

        # Verify and save session
        if session.check_login():
            session.save_session_to_file(SESSION_FILE)
            return AuthResult(
                status="success",
                message="Successfully authenticated with TIDAL",
                authenticated=True,
            )
        else:
            return AuthResult(
                status="error", message="Authentication failed", authenticated=False
            )
    except Exception as e:
        return AuthResult(
            status="error",
            message=f"Authentication error: {str(e)}",
            authenticated=False,
        )


@mcp.tool()
def search_tracks(query: str, limit: int = 10) -> TrackList | ErrorResult:
    """
    Search for tracks on TIDAL.

    Args:
        query: Search query - works best with artist name, song title, or "Artist Song"
        limit: Maximum number of results (default: 10, max: 50)

    Returns:
        List of tracks with id, title, artist, album, and duration
    """
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )

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
        return ErrorResult(message=f"Search failed: {str(e)}")


@mcp.tool()
def get_favorites(limit: int = 20) -> TrackList | ErrorResult:
    """
    Get user's favorite tracks from TIDAL.

    Args:
        limit: Maximum number of tracks to retrieve (default: 20)

    Returns:
        List of favorite tracks
    """
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )

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
        return ErrorResult(message=f"Failed to get favorites: {str(e)}")


@mcp.tool()
def create_playlist(
    name: str, description: str = ""
) -> CreatePlaylistResult | ErrorResult:
    """
    Create a new playlist in your TIDAL account.

    Args:
        name: Name of the playlist
        description: Optional description for the playlist

    Returns:
        Created playlist information including ID and URL
    """
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )

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
        return ErrorResult(message=f"Failed to create playlist: {str(e)}")


@mcp.tool()
def add_tracks_to_playlist(
    playlist_id: str, track_ids: List[str]
) -> AddTracksResult | ErrorResult:
    """
    Add tracks to an existing playlist.

    Args:
        playlist_id: ID of the playlist to add tracks to
        track_ids: List of track IDs to add (from search results)

    Returns:
        Success status and number of tracks added
    """
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )

    try:
        # Get the playlist
        playlist = session.playlist(playlist_id)
        if not playlist:
            return ErrorResult(message=f"Playlist with ID '{playlist_id}' not found")

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
            return ErrorResult(message="Failed to add tracks to playlist")
    except ValueError as e:
        return ErrorResult(message=f"Invalid track ID format: {str(e)}")
    except Exception as e:
        return ErrorResult(message=f"Failed to add tracks: {str(e)}")


@mcp.tool()
def get_user_playlists(limit: int = 20) -> PlaylistList | ErrorResult:
    """
    Get list of user's playlists from TIDAL.

    Args:
        limit: Maximum number of playlists to return (default: 20)

    Returns:
        List of user's playlists with ID, name, description, and track count
    """
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )

    try:
        playlists = session.user.playlists(limit=limit)

        playlist_list = []
        for playlist in playlists:
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
        return ErrorResult(message=f"Failed to get playlists: {str(e)}")


@mcp.tool()
def get_playlist_tracks(
    playlist_id: str, limit: int = 100
) -> PlaylistTracks | ErrorResult:
    """
    Get tracks from a specific playlist.

    Args:
        playlist_id: ID of the playlist
        limit: Maximum number of tracks to return (default: 100)

    Returns:
        List of tracks in the playlist
    """
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )

    try:
        playlist = session.playlist(playlist_id)
        if not playlist:
            return ErrorResult(message=f"Playlist with ID '{playlist_id}' not found")

        # Get tracks from playlist
        playlist_tracks = playlist.tracks(limit=limit)

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
        return ErrorResult(message=f"Failed to get playlist tracks: {str(e)}")


if __name__ == "__main__":
    # Run the server with stdio transport (default for MCP)
    mcp.run()
