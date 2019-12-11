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

def get_data_songkick(metro_areaID):
    try:
        api_key = "kmRJqsmZhyq4LTS5"
        url = "https://api.songkick.com/api/3.0/metro_areas/" + str(metro_areaID) + "/calendar.json?apikey=" + api_key + "&page=1&per_page=20"
        data_r = requests.get(url)
        data = json.loads(data_r.text)
    except: 
        print("Error when reading from url")
        data = {}

    artists = []
    for event in data["resultsPage"]["results"]["event"]:
        for performance in event["performance"]:
            artists.append(performance["displayName"])

    return artists 

london_id = (get_locid_songkick("London"))
london_events = get_data_songkick(london_id)
print(london_events)



