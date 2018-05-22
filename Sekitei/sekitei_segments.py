# -*- coding: utf-8 -*-
import sys
import re
import random
import os
import numpy as np
from collections import Counter
from urlparse import urlparse
from urllib import unquote
from operator import itemgetter
from sklearn.linear_model import LogisticRegression

class Sekitei:
    def __init__(self):
        self.good_features = []
        self.all_features = Counter()
        self.classifier = LogisticRegression()
    def features_to_vector(self, features_url):
        return [float(f in features_url) for f in self.good_features]

def extract_features_from_url(url):
    features = []
    parsed_url = urlparse(unquote(url))
    path, query = parsed_url.path, parsed_url.query
    idx = 0
    
    path_segments = path.split('/')
    
    for seg in path_segments:
        if seg == "":
            continue
        
        # 4a
        # Совпадает со значением <строка> - segment_name_<index>:<string>
        features.append("segment_name_" + str(idx) + ":" + seg)
        sekitei.all_features["segment_name_" + str(idx) + ":" + seg] += 1
        
        # 4b
        # Состоит из цифр - segment_[0-9]_<index>:1
        if re.match(r'[0-9]+$', seg):
            features.append("segment_[0-9]_" + str(idx) + ":1")
            sekitei.all_features["segment_[0-9]_" + str(idx) + ":1"] += 1
            
        # 4c
        # Совпадает со значением <строка с точностью до комбинации цифр>:
        #                                     <строка><цифры><строка> - segment_substr[0-9]_<index>:1
        if re.match(r'[^\d]+\d+[^\d]+$', seg):
            features.append("segment_substr[0-9]_" + str(idx) + ":1")
            sekitei.all_features["segment_substr[0-9]_" + str(idx) + ":1"] += 1
        
        # 4d
        # Имеет заданное расширение - segment_ext_<index>:<extension value>
        matched = re.match(r'(.+)\.(.+)', seg)
        if matched:
            features.append("segment_ext_" + str(idx) + ":" + matched.group(2))
            sekitei.all_features["segment_ext_" + str(idx) + ":" + matched.group(2)] += 1
        
        # 4e
        # Комбинация из двух последних вариантов - segment_ ext_substr[0-9]_<index>:<extension value>
        matched = re.match(r'([^\d]+\d+[^\d]+)\.(\W+)', seg)
        if matched:
            features.append("segment_ ext_substr[0-9]_" + str(idx) + ":" + matched.group(2))
            sekitei.all_features["segment_ ext_substr[0-9]_" + str(idx) + ":" + matched.group(2)] += 1
        
        # 4f
        # Состоит из данного количества символов: segment_len_<index>:<segment length>
        features.append("segment_len_" + str(idx) + ":" + str(len(seg)))
        sekitei.all_features["segment_len_" + str(idx) + ":" + str(len(seg))] += 1

        # Свойства Википедии
        underlines = seg.count('_')
        if underlines:
            features.append("segment_under_" + str(idx) + ":" + str(underlines))
            sekitei.all_features["segment_under_" + str(idx) + ":" + str(underlines)] += 1

        spaces = seg.count(' ')
        if spaces:
            features.append("segment_space_" + str(idx) + ":" + str(spaces))
            sekitei.all_features["segment_space_" + str(idx) + ":" + str(spaces)] += 1

        if ',' in seg:
            features.append("segment_comma_" + str(idx) + ":1")
            sekitei.all_features["segment_comma_" + str(idx) + ":1"] += 1

        if re.search(r'\(.*?\)', seg):
            features.append("segment_syn_" + str(idx) + ":1")
            sekitei.all_features["segment_syn_" + str(idx) + ":1"] += 1
            
        idx += 1
        
    # 1
    # Количество сегментов в пути - segments:<len>
    features.append("segments:" + str(idx))
    sekitei.all_features["segments:" + str(idx)] += 1
        
    query_segments = query.split('&')
    for seg in query_segments:
        if seg == "":
            continue
        # 2, 3
        # Список имен параметров запросной части (может быть пустым) param_name:<имя>
        # Присутствие в запросной части пары <parameters=value> - param:<parameters=value >
        matched = re.match(r'(.+)=(.+)$', seg)
        if matched:
            features.append("param:" + seg)
            sekitei.all_features["param:" + seg] += 1
            features.append("param_name:" + matched.group(1))
            sekitei.all_features["param_name:" + matched.group(1)] += 1
        else:
            features.append("param_name:" + seg)
            sekitei.all_features["param_name:" + seg] += 1
    
    return features

def choose_features(features, threshold):
    return [f for f in features if f[1] > threshold]

def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
    global sekitei
    sekitei = Sekitei()
    
    N, alpha = len(QLINK_URLS) + len(UNKNOWN_URLS), .01

    features_examined = []
    for url in QLINK_URLS:
        features_examined.append(extract_features_from_url(url))
    
    features_general = []
    for url in UNKNOWN_URLS:
        features_general.append(extract_features_from_url(url))
    
    list_of_all_features = []
    list_of_all_features = sekitei.all_features.most_common()
    
    sekitei.good_features = choose_features(list_of_all_features, alpha * N)
    sekitei.good_features = sorted([f[0] for f in sekitei.good_features])

    X = np.asarray(map(sekitei.features_to_vector, features_examined + features_general))
    y = np.asarray([1] * len(QLINK_URLS) + [0] * len(UNKNOWN_URLS))

    sekitei.classifier.fit(X, y)

threshold = 0.55
threshold_step = 0.0005
def fetch_url(url):
    global threshold, threshold_step
    features = extract_features_from_url(url)
    features = sekitei.features_to_vector(features)
    features = np.asarray(features).reshape(1, len(features))
    if sekitei.classifier.predict_proba(features)[0][1] > threshold:
        threshold += threshold_step
        return 1
    else:
        threshold -= threshold_step
        return 0
    return answer