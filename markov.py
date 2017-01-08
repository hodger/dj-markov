#!/usr/bin/env python

from collections import defaultdict
import numpy as np
from random import randint
import json
        
class Markov(object):
    def __init__(self, obj_list=None, load=None):
        self.freq_table = None
        
        self.dict_index = 0
        self.inner_count_index = 0
        self.inner_freq_index = 1
        self.total_index = 1
        
        self.root = None
        self.chain = None
        self.reset()
        if load:
            self.freq_table = json.load(open(load, 'r'))
        if obj_list:
            self.add(obj_list)
    
    #Function for consuming new text to add to existing Markov chain.
    def add(self, obj_list):
        changed_keys = set()
        for i in range(len(obj_list) - 1):
            orig = obj_list[i]
            changed_keys.add(orig)
            after = obj_list[i + 1]
            self._add_pair(orig, after)
        self._calc_frequency(changed_keys=changed_keys)
    
    #Helper function for add_text.
    #Adds a word to the frequency table WITHOUT recalculating frequency value.
    def _add_pair(self, orig, after):
        self.freq_table[orig][self.dict_index][after][self.inner_count_index] += 1
        self.freq_table[orig][self.total_index] += 1
    
    #Calculates frequencies of potential next words for every original word.
    def _calc_frequency(self, changed_keys=None):
        if changed_keys is None:
            changed_keys = list(self.freq_table.keys())
        for k in changed_keys:
            for ik in list(self.freq_table[k][self.dict_index].keys()):
                self.freq_table[k][self.dict_index][ik][self.inner_freq_index] = self.freq_table[k][self.dict_index][ik][self.inner_count_index] / self.freq_table[k][self.total_index]
    
    def reset(self):
        self.freq_table = defaultdict(lambda: [defaultdict(lambda: [0, 0.0]), 0])
        self.root = None
        self.chain = None
    
    def random(self):
        if not self.freq_table:
            raise ValueError("No objects available in frequency table")
        all_objs = list(self.freq_table.keys())
        root = all_objs[randint(0, len(all_objs) - 1)]
        return root
    
    def traverse(self, dist, min_dist=None, root=None, restart_on_error=True):
        if not self.freq_table:
            raise ValueError("No text available")
        if root is None:
            self.root = self.random()
        else:
            self.root = root
        self.chain = self.gen_chain()
        result = []
        chain_index = 0
        while chain_index < dist:
            try:
                result.append(next(self.chain))
                chain_index += 1
            except StopIteration:
                if restart_on_error:
                    if not min_dist is None:
                        if chain_index >= (min_dist - 1):
                            break                    
                    self.root == self.random()
                    self.chain = self.gen_chain()
                    continue
                else:
                    break
        return result
    
    def best(dist, root=None):
        if not self.freq_table:
            raise ValueError("No text available")
        if root is None:
            self.root = self.random()
        else:
            self.root = root
        result = []
        chain_index = 0
        while chain_index < dist:
            item = self.retrieve(root)
            
            chain_index += 1
    
    def gen_chain(self):
        if not self.root:
            raise ValueError("Root has not been set")
        yield self.root
        frequencies = self.retrieve(self.root)
        while frequencies and not ((len(frequencies) == 1) and 
                                                     frequencies[0][0] == None):
            frequencies = self.retrieve(self.root)
            choices = [c for c, w in frequencies]
            weights = [w for c, w in frequencies]
            try:
                new_obj = np.random.choice(choices, size=1, p=weights)[0]
            except ValueError:
                #Weights don't sum to 1. Add a dummy and try again.
                choices.append(None)
                weights.append(1 - sum(weights))
                new_obj = np.random.choice(choices, size=1, p=weights)[0]
            if new_obj is None:
                continue
            else:
                self.root = new_obj
                yield new_obj
        
    def next_objs(self, orig):
        next_objs = list(self.freq_table[orig][self.dict_index].keys())
        return next_objs
    
    #Return a list of tuples in the format of [("next_word", frequency)]
    def retrieve(self, orig):
        freq_list = [(i, self.freq_table[orig][self.dict_index][i]
                                              [self.inner_freq_index]) 
                         for i in self.freq_table[orig][self.dict_index].keys()]
        return freq_list
    
    #Print entire frequency table, prettily.
    def print_table(self):
        for i in list(self.freq_table.keys()):
            self.print_freq(i)
    
    #Print single entry in the frequency table.
    def print_freq(self, orig):
        freq_list = self.retrieve(orig)
        print(orig, ":", freq_list)
    
    def dumps(self):
        for i in self.freq_table:
            print(i, self.freq_table[i])
            
    def consume(target):
        #Iterate over rows of frequency table, borrowing rows with new keys,
        #adjusting and recalculating frequencies of rows with a familiar key. 
        pass
        
    def save(self, name):
        if self.freq_table:
            f = open(name, 'w')
            json.dump(self.freq_table, f)
        else:
            raise ValueError("Cannot save an empty frequency table.")
        
class TextMarkov(Markov):
    def add(self, obj_list):
        if not isinstance(obj_list, str):
            raise ValueError("Object must be str type")
        data = obj_list.split(" ")
        for i in range(len(data) - 1):
            orig = data[i]
            after = data[i + 1]
            self._add_pair(orig, after)
        self._calc_frequency()
        
