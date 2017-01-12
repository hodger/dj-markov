#!/usr/bin/env python

from markov import Markov

chain = Markov(obj_list=['hello', 'world', 'sup', 'hello', 'there', 'sup', 'bro'])
chain.dumps()
chain.dump_totals()
print(chain.traverse(5))
chain.save('test_chain.txt')

print("")
print("")

#copy chain from file
new_chain = Markov(load='test_chain.txt', obj_list=['hello', 'nuts'])
new_chain.dumps()
new_chain.dump_totals()
print(new_chain.traverse(5, force_best=True))
new_chain.dumps()

print("")
print("")

chain.consume(new_chain)
chain.dumps()
chain.dump_totals()
