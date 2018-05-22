# -*- coding: utf-8 -*-
import docreader
import doc2words
import varbyte
import simple9
import pickle
import collections
import mmh3
from struct import pack


args = docreader.parse_command_line().files
reader = docreader.DocumentStreamReader(args[1:])
encoder_name = args[0]

if encoder_name == 'varbyte':
    encoder = varbyte
elif encoder_name == 'simple9':
    encoder = simple9


term_dictionary = collections.defaultdict(list)
url_list = []

for idx, url in enumerate(reader):
    url_list.append(url.url)
    words = doc2words.extract_words(url.text)
    uniq_words = list(set(words))

    for word in uniq_words:
        term_dictionary[word.encode('utf8')].append(idx)

file = open("./urls", "w")
file.write(encoder_name + '\n')
pickle.dump(url_list, file)
file.close()

index = open("./index", "wb")
dict_ = open("./dict", "w")
offset = 0
for key in term_dictionary:
    encoded_str = encoder.encode(term_dictionary[key])
    dict_.write(key + ' ' + str(offset) + '\n')
    index.write(pack('i', len(encoded_str)) + encoded_str)
    offset += len(encoded_str) + 4

index.close()
dict_.close()
