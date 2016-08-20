#!/usr/bin/env python

from collections import defaultdict
from random import randint
from PyLyrics import *
import musicbrainzngs
import sys
import numpy as np
import argparse
import string

class Markov(object):
    #Strip text and create frequency table.
    def __init__(self, initial_text):
        self.freq_table = None
        self.text = ""
        self.chain_index = 0
        self.chain = None
        self.root_word = None
        
        if isinstance(initial_text, str):
            self.add_text(initial_text)
        else:
            #initial_text is a list of strings.
            delim = " "
            self.add_text(delim.join(initial_text))
        
        self.chain = self.gen_chain()
    
    #Recompute markov chain frequencies with new text added.
    def add_text(self, text):
        self.text = self.text + " " + text
        self.freq_table = defaultdict(list)
        
        tokens = [x.strip(",").strip(".") 
                  for x in self.text.strip(" ").split(" ")]
        paired_tokens = []
        
        #pair the tokens.
        for i in range(len(tokens)):
            if i < len(tokens) - 1:
                paired_tokens.append((tokens[i], tokens[i + 1]))
            else:
                paired_tokens.append((tokens[i], None))

        #create a list of potentinal following tokens
        for pair in paired_tokens:
            self.freq_table[pair[0]].append(pair[1])
        
        #calculate frequencies
        for origin, links in self.freq_table.items():
            link_count = len(links)
            token_counts = defaultdict(int)
            for i in links:
                token_counts[i] += 1
            self.freq_table[origin] = [(x, y / link_count) 
                                       for x, y in token_counts.items()]
    
    def compute(self, length, root_word=None, continue_on_error=False):
        self.chain_index = 0
        if root_word is None:
            keys = list(self.freq_table.keys())
            self.root_word = keys[randint(0, len(keys) - 1)]
        else:
            self.root_word = root_word
        result = ""
        try:
            for i in range(length):
                result += next(self.chain) + " "
        except StopIteration:
            pass
        return result
        
    def gen_chain(self):
        if self.chain_index == 0:
            self.chain_index += 1
            yield self.root_word
        frequencies = self.freq_table[self.root_word]
        while(not (len(frequencies) == 1 and frequencies[0][0] == None)):
            #print(self.freq_table[self.root_word])
            frequencies = self.freq_table[self.root_word]
            choices = [c for c, w in frequencies]
            weights = [w for c, w in frequencies]
            try:
                new_word = np.random.choice(choices, size=1, p=weights)[0]
            except ValueError:
                #Weights do not sum to 1, so add a dummy with the difference.
                choices.append(None)
                weights.append(1 - sum(weights))
                new_word = np.random.choice(choices, size=1, p=weights)[0]
            if new_word == None:
                continue
            else:
                self.root_word = new_word
                self.chain_index += 1
                yield new_word       
    
    def print_freq_table(self):
        for key, value in self.freq_table.items():
            print(key, value)

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
    for result in search_results:
        if result['name'] == artist:
            artist_id = result['id']
            print("...found " + result['name'] + ", id: " + artist_id)
            break
    if artist_id == None:
        print("...no artist found with specified name.")
        exit()
    else:
        print("Done.")
    
    print("Searching for " + artist + " albums...")
    
    release_titles = set()
    release_ids = []
    
    for release in musicbrainzngs.browse_releases(
                                      artist=artist_id,
                                      release_type=['album'])['release-list']:
        release_title = release['title']
        release_id = release['id']
        if release['title'] not in release_titles:
            print("...found " + release_title, flush=True)
            release_titles.add(release_title)
            release_ids.append(release_id)
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
        parsed_songs.append(" ".join(lines).replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace(":", ""))
    print("Done.")
    print("Building Markov Chain...")
    markov_chain = Markov(parsed_songs)
    print("Done.")
    #markov_chain.print_freq_table()
    result = markov_chain.compute(150)
    print(result)
    
if __name__ == "__main__":
    main()


