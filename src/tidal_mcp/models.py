"""
Pydantic models for TIDAL MCP Server structured output schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Track(BaseModel):
    """Structured representation of a TIDAL track"""

    id: str = Field(description="Unique track ID")
    title: str = Field(description="Track title")
    artist: str = Field(description="Artist name")
    album: str = Field(description="Album name")
    duration_seconds: int = Field(description="Track duration in seconds")
    url: str = Field(description="TIDAL web URL for the track")


class TrackList(BaseModel):
    """List of tracks with metadata"""

    status: str = Field(description="Operation status (success/error)")
    query: Optional[str] = Field(
        None, description="Search query used (for search results)"
    )
    count: int = Field(description="Number of tracks returned")
    tracks: List[Track] = Field(description="List of track objects")
    message: Optional[str] = Field(None, description="Error message if status is error")


class Playlist(BaseModel):
    """Structured representation of a TIDAL playlist"""

    id: str = Field(description="Unique playlist ID")
    name: str = Field(description="Playlist name")
    description: str = Field(description="Playlist description")
    track_count: int = Field(description="Number of tracks in playlist")
    url: str = Field(description="TIDAL web URL for the playlist")


class PlaylistList(BaseModel):
    """List of playlists with metadata"""

    status: str = Field(description="Operation status (success/error)")
    count: int = Field(description="Number of playlists returned")
    playlists: List[Playlist] = Field(description="List of playlist objects")
    message: Optional[str] = Field(None, description="Error message if status is error")


class PlaylistTracks(BaseModel):
    """Tracks from a specific playlist"""

    status: str = Field(description="Operation status (success/error)")
    playlist_name: str = Field(description="Name of the playlist")
    playlist_id: str = Field(description="ID of the playlist")
    count: int = Field(description="Number of tracks returned")
    tracks: List[Track] = Field(description="List of track objects")
    message: Optional[str] = Field(None, description="Error message if status is error")


class CreatePlaylistResult(BaseModel):
    """Result of creating a new playlist"""

    status: str = Field(description="Operation status (success/error)")
    playlist: Optional[Playlist] = Field(None, description="Created playlist details")
    message: str = Field(description="Status message")


class AddTracksResult(BaseModel):
    """Result of adding tracks to a playlist"""

    status: str = Field(description="Operation status (success/error)")
    playlist_id: str = Field(description="ID of the playlist")
    playlist_name: str = Field(description="Name of the playlist")
    tracks_added: int = Field(description="Number of tracks added")
    playlist_url: str = Field(description="TIDAL web URL for the playlist")
    message: str = Field(description="Status message")


class AuthResult(BaseModel):
    """Result of authentication attempt"""

    status: str = Field(description="Operation status (success/error)")
    message: str = Field(description="Status message")
    authenticated: bool = Field(description="Whether authentication was successful")


class ErrorResult(BaseModel):
    """Error response structure"""

    status: str = Field(
        default="error", description="Always 'error' for error responses"
    )
    message: str = Field(description="Error message describing what went wrong")
