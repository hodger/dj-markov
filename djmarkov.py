#!/usr/bin/env python

from PyLyrics import *
from markov import Markov
import musicbrainzngs
import sys
import argparse
import string

parser = argparse.ArgumentParser(description='Let DJMarkov spit fire in the'
                                           + ' style of your favorite artist.')

parser.add_argument('artist', metavar='artist', type=str, 
                    help='artist whose style DJMarkov will attempt to imitate')

parser.add_argument('song_limit', metavar='song_limit', nargs='?', type=int, 
                    default=None, help='how many songs to use.' 
                                       + ' Defaults to all available songs.')

def main():
    args = parser.parse_args()
    musicbrainzngs.set_useragent("DJMarkov", 1.0)    
    
    artist = args.artist
    limit = args.song_limit
    artist_id = None
    songs = []
    
    print("Searching for artist...")
    
    search_results = musicbrainzngs.search_artists(query=artist)['artist-list']
    if search_results == []:
        print("No results found.")
        exit()
    result_dict = {}
    result_id_count = 0
    for result in search_results:
        if result['name'] == artist:
            result_dict[result_id_count] = result['id']
            message = ""
            try:
                message += str(result_id_count)
                message += " ...found "
                message += result['name']
                message += result['disambiguation']
            except Exception:
                pass
            print(message)
            result_id_count += 1
    if len(result_dict.keys()) == 0:
        print("...no artist found with specified name.")
        exit()
    elif len(result_dict.keys()) == 1:
        artist_id = result_dict[0]
    else:
        user_selection = None
        while(user_selection not in list(result_dict.keys())):
            user_selection = int(input("Please select a number: "))
        artist_id = result_dict[user_selection]
    print("Done.")
    
    print("Searching for " + artist + " albums...")
    
    release_titles = []
    release_ids = []
    
    for release in musicbrainzngs.browse_releases(
                               artist=artist_id,
                               release_type=['album'])['release-list']:
        release_title = release['title'].strip("\'").strip("\"")
        #try:
        #    release_title.encode('utf-8')
        #except Exception:
        #    pass
        #print(release_title + " !")
        if release_title not in release_titles:
            print('...found ' + release_title, flush=True)
            release_titles.append(release_title)
            release_ids.append(release['id'])
    
    for release in musicbrainzngs.browse_releases(
                               artist=artist_id,
                               release_type=['mixtape/street'])['release-list']:
        release_title = release['title'].strip("\'").strip("\"")
        #try:
        #    release_title = release_title.encode('utf-8')
        #except Exception:
        #    pass
        if not release_title in release_titles:
            print('...found ' + str(release_title), flush=True)
            release_titles.append(release_title)
            release_ids.append(release['id'])
    print("Done.")
    
    releases = zip(release_titles, release_ids)
    
    scanned_songs = 0
    stop_scan = False
    for pair in releases:
        release_title = pair[0]
        release_id = pair[1]
        print("Searching for tracks in " + release_title + "...")
        recordings = musicbrainzngs.browse_recordings(
                                           release=release_id)['recording-list']
        for recording_dict in recordings:
            recording_title = recording_dict['title']
            print("...found " + recording_title, end="  ")
            scanned_songs += 1
            try:
                songs.append(PyLyrics.getLyrics(artist, recording_title))
                print("[found lyrics!]")
            except ValueError:
                print("[lyrics unavailable!]")
            if(len(songs) == limit):
                stop_scan = True
                break
        if stop_scan:
            break
    print(str(scanned_songs) + " songs analyzed.")
    print(str(len(songs)) + " songs available.")
    print("Done.")
    
    print("Parsing available songs...")
    parsed_songs = []
    for song in songs:
        lines = song.split("\n")
        parsed_songs.append(" ".join(lines).replace(".", "").replace(",", "")
                                                            .replace("!", "")
                                                            .replace("?", "")
                                                            .replace(":", ""))
    print("Done.")
    print("Building Markov Chain...")
    markov_chain = Markov(" ".join(parsed_songs))
    print("Done.")
    result = markov_chain.traverse(150)
    print(result)
    
if __name__ == "__main__":
    main()


