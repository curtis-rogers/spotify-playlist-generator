import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask App Configuration
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")
app.config["SESSION_COOKIE_NAME"] = "Spotify Login Session"

# Spotify Authentication Setup
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-top-read user-read-recently-played playlist-modify-public playlist-modify-private"
)

def get_spotify_client():
    """Retrieve an authenticated Spotipy client."""
    token_info = session.get("token_info", None)
    if not token_info:
        return None
    
    sp = spotipy.Spotify(auth=token_info["access_token"])
    return sp

@app.route("/")
def login():
    """Redirect user to Spotify for authentication."""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Handle the callback from Spotify after login."""
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("get_user_profile"))

@app.route("/user-profile")
def get_user_profile():
    """Fetch user profile details."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))
    
    user_info = sp.current_user()
    
    return jsonify({
        "id": user_info["id"],
        "display_name": user_info["display_name"],
        "email": user_info.get("email", "N/A"),
        "profile_url": user_info["external_urls"]["spotify"],
        "image": user_info["images"][0]["url"] if user_info["images"] else None
    })


@app.route("/user-top-artists")
def get_top_artists():
    """Fetch user's top artists."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))
    
    results = sp.current_user_top_artists(limit=10, time_range="medium_term")
    
    artists = [
        {
            "id": artist["id"],
            "name": artist["name"],
            "genres": artist["genres"],
            "popularity": artist["popularity"],
            "image": artist["images"][0]["url"] if artist["images"] else None
        }
        for artist in results["items"]
    ]
    
    return jsonify({"top_artists": artists})


@app.route("/user-top-tracks")
def get_top_tracks():
    """Fetch user's top tracks."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))
    
    results = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    
    tracks = [
        {
            "id": track["id"],
            "name": track["name"],
            "artists": [artist["name"] for artist in track["artists"]],
            "album": track["album"]["name"],
            "popularity": track["popularity"],
            "preview_url": track["preview_url"]
        }
        for track in results["items"]
    ]
    
    return jsonify({"top_tracks": tracks})


@app.route("/recently-played")
def get_recently_played():
    """Fetch user's recently played tracks."""
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))
    
    results = sp.current_user_recently_played(limit=10)
    
    tracks = [
        {
            "id": item["track"]["id"],
            "name": item["track"]["name"],
            "artists": [artist["name"] for artist in item["track"]["artists"]],
            "album": item["track"]["album"]["name"],
            "played_at": item["played_at"]
        }
        for item in results["items"]
    ]
    
    return jsonify({"recently_played": tracks})


if __name__ == "__main__":
    app.run(port=8888)
