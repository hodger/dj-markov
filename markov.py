#!/usr/bin/env python

from collections import defaultdict
import numpy as np
from random import randint

class Markov(object):
    def __init__(self, text=None):
        self.freq_table = None
        
        self.dict_index = 0
        self.inner_count_index = 0
        self.inner_freq_index = 1
        self.total_index = 1
        
        self.root_word = None
        self.chain = None
        self.reset()
        if text:
            self.add_text(text)
    
    #Function for consuming new text to add to existing Markov chain.
    def add_text(self, text):
        tokens = text.split(" ")
        for i in range(len(tokens) - 1):
            orig = tokens[i]
            after = tokens[i + 1]
            self.add_word(orig, after)
        self.calc_frequency()
    
    #Helper function for add_text.
    #Adds a word to the frequency table WITHOUT recalculating frequency value.
    def add_word(self, orig, next_word):
        self.freq_table[orig][self.dict_index][next_word][self.inner_count_index] += 1
        self.freq_table[orig][self.total_index] += 1
    
    #Calculates frequencies of potential next words for every original word.
    def calc_frequency(self):
        for k in list(self.freq_table.keys()):
            for ik in list(self.freq_table[k][self.dict_index].keys()):
                self.freq_table[k][self.dict_index][ik][self.inner_freq_index] = self.freq_table[k][self.dict_index][ik][self.inner_count_index] / self.freq_table[k][self.total_index]
    
    def reset(self):
        self.freq_table = defaultdict(lambda: [defaultdict(lambda: [0, 0.0]), 0])
        self.root_word = None
        self.chain = None
    
    def random_word(self):
        if not self.freq_table:
            raise ValueError("No text available")
        all_words = list(self.freq_table.keys())
        root = all_words[randint(0, len(all_words) - 1)]
        return root
    
    def traverse(self, dist, min_dist=None, root_word=None, restart_on_error=True):
        if not self.freq_table:
            raise ValueError("No text available")
        if root_word is None:
            self.root_word = self.random_word()
        else:
            self.root_word = root_word
        self.chain = self.gen_chain()
        result = ""
        chain_index = 0
        while chain_index < dist:
            try:
                result += next(self.chain) + " "
                chain_index += 1
            except StopIteration:
                if restart_on_error:
                    if not min_dist is None:
                        if chain_index >= (min_dist - 1):
                            break                    
                    self.root_word = self.random_word()
                    self.chain = self.gen_chain()
                    continue
                else:
                    break
        return result
    
    def gen_chain(self):
        if not self.root_word:
            raise ValueError("Root word has not been set")
        yield self.root_word
        frequencies = self.retrieve(self.root_word)
        while frequencies and not ((len(frequencies) == 1) and frequencies[0][0] == None):
            frequencies = self.retrieve(self.root_word)
            choices = [c for c, w in frequencies]
            weights = [w for c, w in frequencies]
            try:
                new_word = np.random.choice(choices, size=1, p=weights)[0]
            except ValueError:
                #Weights don't sum to 1. Add a dummy and try again.
                choices.append(None)
                weights.append(1 - sum(weights))
                new_word = np.random.choice(choices, size=1, p=weights)[0]
            if new_word is None:
                continue
            else:
                self.root_word = new_word
                yield new_word
        
    def next_words(self, orig):
        next_words = list(self.freq_table[orig][self.dict_index].keys())
        return next_words
    
    #Return a list of tuples in the format of [("next_word", frequency)]
    def retrieve(self, orig):
        freq_list = [(i, self.freq_table[orig][self.dict_index][i][self.inner_freq_index]) 
                         for i in self.freq_table[orig][self.dict_index].keys()]
        return freq_list
    
    #Print entire frequency table, prettily.
    def print_table(self):
        for i in list(self.freq_table.keys()):
            self.pretty_print_freq(i)
    
    #Print single entry in the frequency table.
    def print_freq(self, orig):
        freq_list = self.retrieve(orig)
        print(orig, ":", freq_list)
