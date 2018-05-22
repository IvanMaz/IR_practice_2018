#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This just a draft for homework 'near-duplicates'
Use MinshinglesCounter to make result closer to checker
"""

import re
import string
from itertools import combinations
from collections import defaultdict

import mmh3

from docreader import *


class TextNormalizer:
    @staticmethod
    def join_numbers(text):
        regex = re.compile('([\d])[\s]+([\d])')
        return regex.sub('\\1\\2', text)

    @staticmethod
    def clean_out_punct(text):
        regex = re.compile('[%s]' % re.escape(string.punctuation + "«" + "»"))
        return regex.sub(' ', text)

    @staticmethod
    def lower_case(text):
        return text.lower()

    @staticmethod
    def remove_entities(text):
        regex = re.compile('&[0-9a-z_A-Z]+;')
        return regex.sub(' ', text)


class MinshinglesCounter:
    SPLIT_RGX = re.compile(r'\w+', re.U)

    def __init__(self, window=5, n=20):
        self.window = window
        self.n = n

    def count(self, text):
        words = MinshinglesCounter._extract_words(text)
        shs = self._count_shingles(words)
        mshs = self._select_minshingles(shs)

        return None if None in mshs else mshs

    def _get_order_function(self, num):
        basis = [1663, 1999, 2203, 2381, 2411,
                 2657, 2789, 2843, 2861, 2909,
                 2953, 3169, 3217, 3259, 3491,
                 3467, 3469, 3499, 3511, 27644437]
        return lambda x: divmod(x, basis[num])[1]

    def _select_minshingles(self, shs):
        """minshingle = [None]*self.n
        for x in shs:
            idx = x % self.n
            minshingle[idx] = x if minshingle[idx] is None else min(
                minshingle[idx], x)

        return [msh for msh in minshingle if msh is not None]"""
        array = [None] * 20
        for shingle in shs:
            for i in range(20):
                if array[i] is None or self._get_order_function(i)(shingle) < self._get_order_function(i)(array[i]):
                    array[i] = shingle
        return array
        """
        YOUR CODE HERE
        """

        """
        use _get_order_function(i) for getting new "permutation"
        use pseudocode from slides
        """
        # return minshingle

    def _count_shingles(self, words):
        shingles = []
        for i in xrange(len(words) - self.window):
            h = mmh3.hash(' '.join(words[i:i+self.window]).encode('utf-8'))
            shingles.append(h)
        return shingles

    @staticmethod
    def _extract_words(text):
        words = re.findall(MinshinglesCounter.SPLIT_RGX, text)
        return words


def broder(docs_to_shingles):
    # group by file

    pairs = []
    for doc in docs_to_shingles:
        for idx, shingle in enumerate(docs_to_shingles[doc]):
            pairs.append(tuple([str(idx+1) + '_' + str(shingle), doc]))
    
    group_by_shingle = defaultdict(list)
    for pair in pairs:
        group_by_shingle[pair[0]].append(pair[1])

    # merge
    docs_pairs = defaultdict(int)
    for shingle in group_by_shingle:
        if len(group_by_shingle[shingle]) > 1:
            for pair in combinations(group_by_shingle[shingle], 2):
                docs_pairs[tuple(sorted(pair))] += 1

    for pair in docs_pairs:
        n = docs_pairs[pair]
        #JC = n * 1. / (n + 2 * (20 - n))
        JC = n * 1. / 20
        if JC > 0.75:
            print "{0} {1} {2}".format(pair[0], pair[1], JC)


def main():
    files = sys.argv[1:]  # all input files in current test case
    minshingles_counter = MinshinglesCounter(window=5, n=20)

    docs_to_shingles = {}
    for path in files:
        for doc in DocumentStreamReader(path):
            if doc.url not in docs_to_shingles:
                text = doc.text
                text = TextNormalizer.join_numbers(text) # replace '40 000' with '40000'
                text = TextNormalizer.remove_entities(text) # replace '&nbsp;', '&amp;' and other entities with whitespace
                text = TextNormalizer.clean_out_punct(text) # remove punctuation
                text = TextNormalizer.lower_case(text) # lower case of the whole text
                mnsh = minshingles_counter.count(text)
                if not mnsh is None:
                    docs_to_shingles[doc.url] = mnsh

    broder(docs_to_shingles)

    """
    YOUR CODE HERE
    """

    """
    use DocumentStremReader for reading input data; look for example in docreader.py:main
    """
    """
    Hint: check whether this doc is already known and does it have any valid content
    """
    """
    normalize text:
        text = doc.text
        text = TextNormalizer.join_numbers(text) # replace '40 000' with '40000'
        text = TextNormalizer.remove_entities(text) # replace '&nbsp;', '&amp;' and other entities with whitespace
        text = TextNormalizer.clean_out_punct(text) # remove punctuation
        text = TextNormalizer.lower_case(text) # lower case of the whole text
    """
    """
    Remember: there should be only pairs of duplicates in output.
        measure = float(broder_cnt) / 20.
        if measure > .75:
            print doc1, doc2, measure
    """

    """
    GOOD LUCK! :)
    """


if __name__ == '__main__':
    main()
