"""
Lightweight Spotify integration helpers for recommendations.
This module uses the Client Credentials flow for recommendations and
provides a simple `recommend_for_mood` function that returns a short
list of tracks (name, artist, preview_url, external_url).

In production you'd want proper user OAuth if you need playback control.
"""

import os
import base64
import httpx
from typing import List, Dict
import config

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_RECOMMEND_URL = "https://api.spotify.com/v1/recommendations"


async def _get_app_token() -> str:
    """Obtain an app-level access token (client credentials)."""
    client_id = os.getenv("SPOTIFY_CLIENT_ID") or getattr(config, "SPOTIFY_CLIENT_ID", None)
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET") or getattr(config, "SPOTIFY_CLIENT_SECRET", None)
    if not client_id or not client_secret:
        raise RuntimeError("Spotify client id/secret not configured")

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
        resp.raise_for_status()
        j = resp.json()
        return j.get("access_token")


async def recommend_for_mood(mood: str, limit: int = 6) -> List[Dict]:
    """Return a list of recommended tracks for a given mood.

    Uses simple mapping from mood -> target_audio_features/seed_genres.
    """
    token = await _get_app_token()

    # Map moods to seeds / target features (simple heuristics)
    mood_map = {
        "happy": {"seed_genres": "pop,feel-good", "target_valence": 0.9, "target_tempo": 110},
        "calm": {"seed_genres": "acoustic,ambient", "target_valence": 0.6, "target_tempo": 70},
        "anxious": {"seed_genres": "chill,ambient", "target_valence": 0.4, "target_tempo": 60},
        "depressed": {"seed_genres": "singer-songwriter,acoustic", "target_valence": 0.35, "target_tempo": 60},
        "sad": {"seed_genres": "piano,acoustic", "target_valence": 0.3, "target_tempo": 60},
        "angry": {"seed_genres": "rock,metal", "target_valence": 0.4, "target_tempo": 120}
    }

    params = {"limit": str(limit)}
    seed = mood_map.get(mood, {})
    if seed:
        params.update({"seed_genres": seed.get("seed_genres")})
        # map audio feature targets if present
        if seed.get("target_valence"):
            params["target_valence"] = str(seed["target_valence"])  # 0.0 - 1.0
        if seed.get("target_tempo"):
            params["target_tempo"] = str(seed["target_tempo"])  # BPM

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(SPOTIFY_RECOMMEND_URL, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    tracks = []
    for t in data.get("tracks", [])[:limit]:
        artists = ", ".join([a["name"] for a in t.get("artists", [])])
        tracks.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "artists": artists,
            "preview_url": t.get("preview_url"),
            "external_url": t.get("external_urls", {}).get("spotify")
        })

    return tracks


async def search_tracks(query: str, limit: int = 8) -> List[Dict]:
    """Simple search helper using Spotify Search endpoint (uses app token)."""
    token = await _get_app_token()
    url = "https://api.spotify.com/v1/search"
    params = {"q": query, "type": "track", "limit": str(limit)}
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    tracks = []
    for t in data.get("tracks", {}).get("items", []):
        artists = ", ".join([a["name"] for a in t.get("artists", [])])
        tracks.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "artists": artists,
            "preview_url": t.get("preview_url"),
            "external_url": t.get("external_urls", {}).get("spotify")
        })

    return tracks
