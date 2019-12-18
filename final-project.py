import requests
import sqlite3
import json
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re


def get_locid_songkick(loc):
    try: 
        api_key = "kmRJqsmZhyq4LTS5"
        loc_query = loc + "&apikey=" + api_key
        loc_url = "https://api.songkick.com/api/3.0/search/locations.json?query=" + loc_query
        loc_r = requests.get(loc_url)
        info = json.loads(loc_r.text)
        return info, info["resultsPage"]["results"]["location"][0]["metroArea"]["id"]
    except: 
        print("Error when reading from url location")
        pass

def get_data_songkick(metro_areaID):
    try:
        api_key = "kmRJqsmZhyq4LTS5"
        url = "https://api.songkick.com/api/3.0/metro_areas/" + str(metro_areaID) + "/calendar.json?apikey=" + api_key + "&page=1&per_page=20"
        data_r = requests.get(url)
        data = json.loads(data_r.text)
        artists = []
        for event in data["resultsPage"]["results"]["event"]:
            artists.append(event["performance"][0]["displayName"])
        return data, artists 
    except: 
        print("Error when reading from url metro id")
        pass

    

def musixmatch_artist_search(artist):
    try:
        api_key = "ca6e551b9b248119f6d8bd4c56d39613"
        url = "https://api.musixmatch.com/ws/1.1/artist.search?q_artist=" + artist + "&page_size=1&apikey=" + api_key
        artist_search = requests.get(url)
        # print(artist_search.text)
        artist_info = json.loads(artist_search.text)
        if len(artist_info["message"]["body"]["artist_list"]) == 0:
            pass
        else:
            artist_id = str(artist_info["message"]["body"]["artist_list"][0]["artist"]["artist_id"])
            artist_rating = artist_info["message"]["body"]["artist_list"][0]["artist"]["artist_rating"]
            return artist_info, artist_id, artist_rating
    except:
        print("Error when reading from url artist id")
        pass

    
def album_get(artist_id):
    try:
        api_key = "ca6e551b9b248119f6d8bd4c56d39613"
        url = "https://api.musixmatch.com/ws/1.1/artist.albums.get?artist_id=" + artist_id +"&g_album_name=1&page=1&page_size=1&apikey=" + api_key
        album_search = requests.get(url)
        # print(album_search.text)
        album_info = json.loads(album_search.text)
        if len(album_info["message"]["body"]["album_list"][0]["album"]["primary_genres"]["music_genre_list"]) == 0:
            return album_info, "No genre"
        else:
            return album_info, album_info["message"]["body"]["album_list"][0]["album"]["primary_genres"]["music_genre_list"][0]["music_genre"]["music_genre_name"]
    except:
        print("Error when reading from url genre")
        pass


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
    cur.execute('CREATE TABLE IF NOT EXISTS SongkickDATA(event_name TEXT, head_artist TEXT, event_id INTEGER, city TEXT, metroarea_id INTEGER, metroarea_name TEXT)')

    for event in data['resultsPage']['results']['event']:
        _event_name = event['displayName']
        _head_artist = event['performance'][0]['displayName']
        _event_id = event['id']
        _city = event['location']['city']
        _metroarea_id = event['venue']['metroArea']['id']
        _metroarea_name = event['venue']['metroArea']['displayName'].split(' (')[0]
        cur.execute('INSERT INTO SongkickDATA (event_name, head_artist, event_id, city, metroarea_id, metroarea_name) VALUES (?, ?, ?, ?, ?, ?)',
                 (_event_name, _head_artist, _event_id, _city, _metroarea_id, _metroarea_name))

    conn.commit()

def setupMMsearchTable(data):
    conn = sqlite3.connect('desktop/final206/finalapi.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS musixmatch_artists(artist_name TEXT UNIQUE, artist_id INTEGER, artist_rating INTEGER)')

    for artist in data['message']['body']['artist_list']:
        _artist_name = artist['artist']['artist_name']
        _artist_id = artist['artist']['artist_id']
        _artist_rating = artist['artist']['artist_rating']
        cur.execute('INSERT OR IGNORE INTO musixmatch_artists (artist_name, artist_id, artist_rating) VALUES (?, ?, ?)',
                 (_artist_name, _artist_id, _artist_rating))

    conn.commit()

def setupGenreTable(data):
    conn = sqlite3.connect('desktop/final206/finalapi.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS musixmatch_genre(artist_name TEXT UNIQUE, genre_name TEXT)')

    _artist_name = data[0]['message']['body']['album_list'][0]['album']['artist_name']
    _genre_name = data[1]
    cur.execute('INSERT OR IGNORE INTO musixmatch_genre (artist_name, genre_name) VALUES (?, ?)',
            (_artist_name, _genre_name))

    conn.commit()

def get_category_dict(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()

    loc_cat_dict = {}
    final_dict = {}
    cur.execute("SELECT musixmatch_genre.genre_name, SongkickDATA.metroarea_name FROM SongkickDATA JOIN musixmatch_genre ON SongkickDATA.head_artist = musixmatch_genre.artist_name")

    fetched = cur.fetchall()

    for met_id in fetched:
        if met_id[1] in loc_cat_dict:
            loc_cat_dict[met_id[1]].append(met_id[0])
        else:
            loc_cat_dict[met_id[1]] = [met_id[0]]
    
    for location in loc_cat_dict:
        loc_genre = {}
        for genre in loc_cat_dict[location]:
            loc_genre[genre] = loc_genre.get(genre, 0) + 1
        final_dict[location] = loc_genre

    return final_dict

def write_to_file(data):
    with open('desktop/final206/calculations.txt', 'w') as file:    
        file.write(json.dumps(data, indent=3))
        file.close()
        
def bar_chart(final_dict, loc_list):
    # get big list of sorted data
    big_list = []
    for key1, value1 in final_dict.items():
        sortedlist = sorted(value1.items(), key=lambda kv: kv[1], reverse=True)
        # print(sortedlist)
        big_list.append(sortedlist)
    # return(big_list)

    # get data for 7644 aka New York in a list
    ny_cat = []
    ny_num = []
    for tup in big_list[0]:
        ny_cat.append(tup[0])
        ny_num.append(tup[1])

    
    # get data for 18076 aka Detroit in a list
    d_cat = []
    d_num = []
    for tup in big_list[1]:
        d_cat.append(tup[0])
        d_num.append(tup[1])
   
    # get data for 17835 aka Los Angeles in a list
    la_cat = []
    la_num = []
    for tup in big_list[2]:
        la_cat.append(tup[0])
        la_num.append(tup[1])
   
    # get data for 2846 aka Seattle in a list
    s_cat = []
    s_num = []
    for tup in big_list[3]:
        s_cat.append(tup[0])
        s_num.append(tup[1])

    # get data for 2846 aka Boston in a list
    b_cat = []
    b_num = []
    for tup in big_list[4]:
        b_cat.append(tup[0])
        b_num.append(tup[1])

    # get data for 2846 aka Cincinatti in a list
    cin_cat = []
    cin_num = []
    for tup in big_list[5]:
        cin_cat.append(tup[0])
        cin_num.append(tup[1])

    # get data for 2846 aka San Francisco in a list
    sf_cat = []
    sf_num = []
    for tup in big_list[6]:
        sf_cat.append(tup[0])
        sf_num.append(tup[1])

    # Initialize the plot
    fig = plt.figure(figsize=(20,6))
    
    # plt.xticks(rotation=90)
    plt.tight_layout()
    plt.suptitle('Most popular Genres in Metro Area According to SongKick Events')
    
    ax1 = fig.add_subplot(421)
    ax2 = fig.add_subplot(422)
    ax3 = fig.add_subplot(423)
    ax4 = fig.add_subplot(424)
    ax5 = fig.add_subplot(425)
    ax6 = fig.add_subplot(426)
    ax7 = fig.add_subplot(427)

    axis_list = [ax1,ax2,ax3,ax3,ax5,ax6,ax7]

    # plot the data
    ax1.bar(ny_cat, ny_num)
    ax2.bar(d_cat, d_num)
    ax3.bar(la_cat, la_num)
    ax4.bar(s_cat, s_num)
    ax5.bar(b_cat, b_num)
    ax6.bar(cin_cat, cin_num)
    ax7.bar(sf_cat, sf_num)   

    # label x and y labels
    ax1.tick_params(labelrotation=20)
    # ax1.set_xlabel('Genre Catagories', fontsize=10)
    # ax1.set_ylabel('Number of Events', fontsize=10)
    
    ax2.tick_params(labelrotation=20)
    # ax2.set_xlabel('Genre Catagories', fontsize=10)
    # ax2.set_ylabel('Number of Events', fontsize=10)
 
    ax3.tick_params(labelrotation=20)
    # ax3.set_xlabel('Genre Catagories', fontsize=10)
    # ax3.set_ylabel('Number of Events', fontsize=10)

    ax4.tick_params(labelrotation=20)
    # ax4.set_xlabel('Genre Catagories', fontsize=10)
    # ax4.set_ylabel('Number of Events', fontsize=10)
  
    ax5.tick_params(labelrotation=20)
    # ax5.set_xlabel('Genre Catagories', fontsize=10)
    # ax5.set_ylabel('Number of Events', fontsize=10)
    
    ax6.tick_params(labelrotation=20)
    # ax6.set_xlabel('Genre Catagories', fontsize=10)
    # ax6.set_ylabel('Number of Events', fontsize=10)

    ax7.tick_params(labelrotation=20)
    # ax7.set_xlabel('Genre Catagories', fontsize=10)
    # ax7.set_ylabel('Number of Events', fontsize=10)
  

    # add titles
    for axis in axis_list:
        axis.set_title(loc_list[axis_list.index(axis)], fontsize =10)
        

    plt.show()

def get_percentages_genres(final_dict):
    all_genres_count = {}
    genres_percentages = {}
    
    for city in final_dict:
        for genre in final_dict[city]:
                all_genres_count[genre] = all_genres_count.get(genre, 0) + 1

    total = sum(all_genres_count.values())

    for genre in all_genres_count:
        genres_percentages[genre] = all_genres_count[genre]/total
    
    return genres_percentages

def make_pie(percentages):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = list(percentages.keys())
    sizes = list(percentages.values())
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 6})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()




def main():
    # print("================================STARTING NEW==============================")
    locations = ["New York", "Detroit", "Los Angeles", "Seattle", "Boston", "Cincinatti", "San Francisco"]
    # for location in locations:
    #     locID = get_locid_songkick(location)
    #     setUpSKlcdTable(locID[0])
    #     info = get_data_songkick(locID[1])
    #     # print(info)
    #     setUpSKlcdDATA(info[0])
    #     for artist in info[1]:
    #         artist_info = musixmatch_artist_search(artist)
    #         if artist_info == None:
    #             continue
    #         artist_genre = album_get(artist_info[1])    
    #         if artist_genre == None:
    #             continue
    #         setupMMsearchTable(artist_info[0])
    #         setupGenreTable(artist_genre)

    fin_dict = get_category_dict('finalapi.sqlite')
    write_to_file(fin_dict)
    bar_chart(fin_dict,locations)
    percent_list = get_percentages_genres(fin_dict)
    make_pie(percent_list)

main()
