# -*- coding: utf-8 -*-
import pickle
import varbyte
import simple9
import qtree
import numpy as np
import mmh3
import time
from struct import unpack


def intersec(term1, term2):
    return np.intersect1d(term1, term2, True)


def union(term1, term2):
    return np.union1d(term1, term2)

def get_id_array(word):
    offset = word_to_offset[word]
    file.seek(offset)
    length = unpack('i', file.read(4))[0]
    ids = file.read(length)
    return ids


def search(root):
    if root.is_term:
        return np.asarray(encoder.decode(get_id_array(root.value)))
    elif root.is_operator:
        if root.value == '&':
            return intersec(search(root.left), search(root.right))
        elif root.value == '|':
            return union(search(root.left), search(root.right))
        elif root.value == '!':
            return np.setdiff1d(np.arange(len(url_list)), np.asarray(search(root.left if root.left else root.right)), True)

#start = time.time()

file = open("./urls", "r")

encoder_name = file.readline()
url_list = pickle.load(file)

file.close()
#end = time.time()
#print "urls_time: ", end - start

#print "url_size: ", len(url_list)
#start = time.time()
file = open("./dict", "r")

word_to_offset = {}
for line in file.read().split('\n')[:-1]:
    lsp = line.split(' ')
    word_to_offset[lsp[0]] = int(lsp[1])

file.close()
#end = time.time()
#print "dict_time: ", end - start

file = open("./index", "rb")

if encoder_name[:-1] == 'varbyte':
    encoder = varbyte
elif encoder_name[:-1] == 'simple9':
    encoder = simple9

while True:
    try:
        line = raw_input()
        tree = qtree.parse_query(line.decode('utf-8').lower())
        res = search(tree)
        print line
        print len(res)
        for idx in res:
            print url_list[idx]
    except:
        break
