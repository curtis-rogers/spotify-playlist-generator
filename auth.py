import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="proj.env")


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_COOKIE_NAME"] = "Spotify Login Session"





# Spotify Authentication
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-library-read playlist-read-private"
)

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
    return redirect(url_for("get_user_playlists"))

@app.route("/playlists")
def get_user_playlists():
    """Fetch user's Spotify playlists."""
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect("/")
    
    sp = spotipy.Spotify(auth=token_info["access_token"])
    playlists = sp.current_user_playlists()
    
    return {"playlists": playlists}

if __name__ == "__main__":
    app.run(port=8888)
