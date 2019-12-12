import requests
import sqlite3
import json
import spotipy
import sys
import pprint



def get_locid_songkick(loc):
    try: 
        api_key = "kmRJqsmZhyq4LTS5"
        loc_query = loc + "&apikey=" + api_key
        loc_url = "https://api.songkick.com/api/3.0/search/locations.json?query=" + loc_query
        loc_r = requests.get(loc_url)
        info = json.loads(loc_r.text)
        return info, info["resultsPage"]["results"]["location"][0]["metroArea"]["id"]
    except: 
        print("Error when reading from url")
        info = {}

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
        artists.append(event["performance"][0]["displayName"])

    return data, artists 

def musixmatch_artist_search(artist):
    api_key = "ca6e551b9b248119f6d8bd4c56d39613"
    url = " https://api.musixmatch.com/ws/1.1/artist.search?q_artist=" + artist + "&page_size=1&apikey=" + api_key
    artist_search = requests.get(url)
    artist_info = json.loads(artist_search.text)
    return str(artist_info["message"]["body"]["artist_list"][0]["artist"]["artist_id"])


def musixmatch_artist_get(artist_id):
    api_key = "ca6e551b9b248119f6d8bd4c56d39613"
    url = " https://api.musixmatch.com/ws/1.1/artist.get?artist_id=" + artist_id + "&page_size=1&apikey=" + api_key
    artistID_search = requests.get(url)
    artist_info = json.loads(artistID_search.text)
    return artist_info

def setUpSKlcdTable(data):
    conn = sqlite3.connect('/Users/Yasmeen/Desktop/final206/songkicklcd.sqlite')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS SongkickLCD')
    cur.execute('CREATE TABLE SongkickLCD(city_name TEXT, city_country TEXT, id INTEGER)')

    for result in data['resultsPage']['results']['location']:
        _city_name = result['city']['displayName']
        _city_country = result['city']['country']['displayName']
        _id = result['metroArea']['id']
        cur.execute('INSERT INTO SongkickLCD (city_name, city_country, id) VALUES (?, ?, ?)',
                 (_city_name, _city_country, _id))

    conn.commit()




def main():
    london_id = (get_locid_songkick("London"))
    london_events = get_data_songkick(london_id[1])
    print(london_events[1])
    keshaID = musixmatch_artist_search('asap rocky')
    print(musixmatch_artist_get(keshaID))
    setUpSKlcdTable(london_id[0])

main()
