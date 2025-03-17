import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

import requests
from io import BytesIO
from PIL import Image

def getSongInfo():
  scope = 'user-read-currently-playing'
  sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=60)
  result = sp.current_user_playing_track()

  if result is None:
      print("No song playing")
  else:  
    song = result["item"]["name"]
    artist = result["item"]["artists"][0]["name"]
    imageURL = result["item"]["album"]["images"][0]["url"]
    uri_details = result["item"]["uri"]
    return [song, imageURL, artist, uri_details]
