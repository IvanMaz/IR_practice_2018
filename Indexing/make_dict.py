# -*- coding: utf-8 -*-
"""import pickle

index = open("./index", "rb")
off_dict = open("./dict", "wb")

lines = index.read().split('\r\n\n')

offset = 0
for idx, line in enumerate(lines[:-1]):
    word, docs  = line.split(' ', 1)
    off_dict.write(word + ' ' + str(offset) + '\n')
    offset += len(line)

index.close()
off_dict.close()"""