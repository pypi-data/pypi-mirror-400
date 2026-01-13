# spotify-tools

A Python library for interacting with the Spotify API.

## Installation

```bash
pip install spotify-tools
```

## Features

- Simple client wrapper around `spotipy` with OAuth authentication
- Pydantic schemas for Spotify API responses
- Playlist management (create, update, get tracks)
- Track search with fuzzy matching support

## Usage

```python
from spotify_tools import Client, search_track_fuzzy, get_playlist_tracks

# Create a client (uses environment variables for credentials)
client = Client()

# Search for a track with fuzzy matching
track, score = search_track_fuzzy(client, "Song Title", "Artist Name")

# Get all tracks from a playlist
tracks = get_playlist_tracks(client, "playlist_id")
```

## Configuration

Set the following environment variables:

- `SPOTIFY_CLIENT_ID` - Your Spotify app client ID
- `SPOTIFY_CLIENT_SECRET` - Your Spotify app client secret
- `SPOTIFY_REDIRECT_URI` - OAuth redirect URI (default: `http://localhost:8080`)

## License

GPL-3.0-or-later

