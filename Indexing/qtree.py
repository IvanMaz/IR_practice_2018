# -*- coding: utf-8 -*-
import re
import unittest


SPLIT_RGX = re.compile(r'\w+|[\(\)&\|!]', re.U)


class QtreeTypeInfo:
    def __init__(self, value, op=False, bracket=False, term=False):
        self.value = value
        self.is_operator = op
        self.is_bracket = bracket
        self.is_term = term

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if isinstance(other, QtreeTypeInfo):
            return self.value == other.value
        return self.value == other


class QTreeTerm(QtreeTypeInfo):
    def __init__(self, term):
        QtreeTypeInfo.__init__(self, term, term=True)


class QTreeOperator(QtreeTypeInfo):
    def __init__(self, op):
        QtreeTypeInfo.__init__(self, op, op=True)
        self.priority = get_operator_prio(op)
        self.left = None
        self.right = None


class QTreeBracket(QtreeTypeInfo):
    def __init__(self, bracket):
        QtreeTypeInfo.__init__(self, bracket, bracket=True)


def get_operator_prio(s):
    if s == '|':
        return 0
    if s == '&':
        return 1
    if s == '!':
        return 2

    return None


def is_operator(s):
    return get_operator_prio(s) is not None


def tokenize_query(q):
    tokens = []
    for t in map(lambda w: w.encode('utf-8'), re.findall(SPLIT_RGX, q)):
        if t == '(' or t == ')':
            tokens.append(QTreeBracket(t))
        elif is_operator(t):
            tokens.append(QTreeOperator(t))
        else:
            tokens.append(QTreeTerm(t))

    return tokens


def build_query_tree(tokens):
    root = None
    depth = 0
    min_depth = len(tokens)
    min_prio = 3
    pos = 0
    for idx, token in enumerate(tokens):
        if is_operator(token):
            if (depth < min_depth) or (get_operator_prio(token) <= min_prio and depth == min_depth):
                min_depth = depth
                min_prio = get_operator_prio(token)
                root = token
                pos = idx
        elif token.value == '(':
            depth += 1
        elif token.value == ')':
            depth -= 1
    if root is None:
        for token in tokens:
            if not token.is_bracket:
                return token
    else:
        root.left = build_query_tree(tokens[:pos])
        root.right = build_query_tree(tokens[pos + 1:])
    return root


def parse_query(q):
    tokens = tokenize_query(q)
    return build_query_tree(tokens)
