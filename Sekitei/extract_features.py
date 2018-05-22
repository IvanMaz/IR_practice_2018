# -*- coding: utf-8 -*-
import sys
import re
import random
import numpy as np
from collections import Counter
from urlparse import urlparse
from urllib import unquote
from operator import itemgetter

def extract_features_from_url(url, features):
    parsed_url = urlparse(unquote(url))
    path, query = parsed_url.path, parsed_url.query
    idx = 0
    
    path_segments = path.split('/')
    
    for seg in path_segments:
        if seg == "":
            continue
        
        # 4a
        # Совпадает со значением <строка> - segment_name_<index>:<string>
        features["segment_name_" + str(idx) + ":" + seg] += 1
        
        # 4b
        # Состоит из цифр - segment_[0-9]_<index>:1
        if re.match(r'[0-9]+$', seg):
            features["segment_[0-9]_" + str(idx) + ":1"] += 1
        
        # 4c
        # Совпадает со значением <строка с точностью до комбинации цифр>:
        #                                     <строка><цифры><строка> - segment_substr[0-9]_<index>:1
        if re.match(r'[^\d]+\d+[^\d]+$', seg):
            features["segment_substr[0-9]_" + str(idx) + ":1"] += 1
        
        # 4d
        # Имеет заданное расширение - segment_ext_<index>:<extension value>
        matched = re.match(r'(.+)\.(.+)', seg)
        if matched:
            features["segment_ext_" + str(idx) + ":" + matched.group(2)] += 1
        
        # 4e
        # Комбинация из двух последних вариантов - segment_ ext_substr[0-9]_<index>:<extension value>
        matched = re.match(r'([^\d]+\d+[^\d]+)\.(\W+)', seg)
        if matched:
            features["segment_ ext_substr[0-9]_" + str(idx) + ":" + matched.group(2)] += 1
        
        # 4f
        # Состоит из данного количества символов: segment_len_<index>:<segment length>
        features["segment_len_" + str(idx) + ":" + str(len(seg))] += 1
        
        idx += 1
        
    # 1
    # Количество сегментов в пути - segments:<len>
    features["segments:" + str(idx)] += 1
    
    query_segments = query.split('&')
    for seg in query_segments:
        if seg == "":
            continue
        # 2, 3
        # Список имен параметров запросной части (может быть пустым) param_name:<имя>
        # Присутствие в запросной части пары <parameters=value> - param:<parameters=value >
        matched = re.match(r'(.+)=(.+)$', seg)
        if matched:
            features["param:" + seg] += 1
            features["param_name:" + matched.group(1)] += 1
        else:
            features["param_name:" + seg] += 1

def extract_features_from_files(examined_file, general_file):
    examined_links = []
    with open(examined_file, "r") as examined:
        for line in examined:
            examined_links.append(line[:-1])
    
    general_links = []
    with open(general_file, "r") as general:
        for line in general:
            general_links.append(line[:-1])
    
    examined.close()
    general.close()
    
    return examined_links, general_links

def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
    sample_size = 1000
    alpha = 0.1
    features = Counter()
    
    examined_links, general_links = extract_features_from_files(INPUT_FILE_1, INPUT_FILE_2)
    
    for url in np.random.permutation(examined_links)[:sample_size]:
        extract_features_from_url(url, features)
    for url in np.random.permutation(general_links)[:sample_size]:
        extract_features_from_url(url, features)
    
    with open(OUTPUT_FILE, 'w') as output:
        threshold = alpha * sample_size
        for feature, count in features.items():
            if count > threshold:
                output.write(feature + '\t' + str(count) + '\n')
    output.close
