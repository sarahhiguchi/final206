import requests
import sqlite3
import json



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
    try:
        api_key = "ca6e551b9b248119f6d8bd4c56d39613"
        url = " https://api.musixmatch.com/ws/1.1/artist.search?q_artist=" + artist + "&page_size=1&apikey=" + api_key
        artist_search = requests.get(url)
        artist_info = json.loads(artist_search.text)
    except:
        print("Error when reading from url")
        artist_info = {}

    return artist_info, str(artist_info["message"]["body"]["artist_list"][0]["artist"]["artist_id"])


def album_get(artist_id):
    try:
        api_key = "ca6e551b9b248119f6d8bd4c56d39613"
        url = " https://api.musixmatch.com/ws/1.1/artist.albums.get?artist_id=" + artist_id +"&g_album_name=1&page=1&page_size=1&apikey=" + api_key
        album_search = requests.get(url)
        album_info = json.loads(album_search.text)
    except:
        print("Error when reading from url")
        album_info = {}

    return album_info["message"]["body"]["album_list"][0]["album"]["primary_genres"]["music_genre_list"]

def setUpSKlcdTable(data):
    conn = sqlite3.connect('desktop/final206/finalapi.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS SongkickLCD(city_name TEXT, city_country TEXT, metroarea_id INTEGER)')

    for result in data['resultsPage']['results']['location']:
        _city_name = result['city']['displayName']
        _city_country = result['city']['country']['displayName']
        _metroarea_id = result['metroArea']['id']
        cur.execute('INSERT INTO SongkickLCD (city_name, city_country, metroarea_id) VALUES (?, ?, ?)',
                 (_city_name, _city_country, _metroarea_id))

    conn.commit()


def setUpSKlcdDATA(data):
    conn = sqlite3.connect('desktop/final206/finalapi.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS SongkickDATA(event_name TEXT, head_artist TEXT, event_id INTEGER)')

    for event in data['resultsPage']['results']['event']:
        _event_name = event['displayName']
        _head_artist = event['performance'][0]['displayName']
        _event_id = event['id']
        cur.execute('INSERT INTO SongkickDATA (event_name, head_artist, event_id) VALUES (?, ?, ?)',
                 (_event_name, _head_artist, _event_id))

    conn.commit()

# def setUpSKlcdDATA(data):
#     conn = sqlite3.connect('desktop/final206/finalapi.sqlite')
#     cur = conn.cursor()
#     cur.execute('CREATE TABLE IF NOT EXISTS musixmatch_artists(event_name TEXT, head_artist TEXT, event_id INTEGER)')

#     for event in data['resultsPage']['results']['event']:
#         _event_name = event['displayName']
#         _head_artist = event['performance'][0]['displayName']
#         _event_id = event['id']
#         cur.execute('INSERT INTO SongkickDATA (event_name, head_artist, event_id) VALUES (?, ?, ?)',
#                  (_event_name, _head_artist, _event_id))

#     conn.commit()


def main():
    locations = ["New York", "Detroit", "Chicago", "Los Angeles", "Seattle"]
    for location in locations:
        locID = get_locid_songkick(location)
        setUpSKlcdTable(locID[0])
        info = get_data_songkick(locID[1])
        setUpSKlcdDATA(info[0])
        for artist in info[1]:
            artist_info = musixmatch_artist_search(artist)
            artist_genre = album_get(artist_info[1])
            print(artist_info, artist_genre)
    


main()
