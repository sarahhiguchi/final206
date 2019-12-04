import requests


spotify_clientID="c2120610f7f4473781820928004f3760" 
response = requests.get("https://api.spotify.com/v1/artists/{id}/top-tracks")