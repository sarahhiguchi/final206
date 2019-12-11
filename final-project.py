import requests
import spotipy
import sqlite3
import json


def get_locid_songkick(loc):
    try: 
        api_key = "kmRJqsmZhyq4LTS5"
        loc_query = loc + "&apikey=" + api_key
        loc_url = "https://api.songkick.com/api/3.0/search/locations.json?query=" + loc_query
        loc_r = requests.get(loc_url)
        info = json.loads(loc_r.text)
        return info["resultsPage"]["results"]["location"][0]["metroArea"]["id"]
    except: 
        print("Error when reading from url")
        info = {}
    return info

def get_data_songkick

print(get_locid_songkick("London"))


