# -*- coding: utf-8 -*-
from struct import pack, unpack


def vb_encode_number(n):
    bytes = []
    while 1:
        bytes.insert(0, n % 128)
        if n < 128:
            break
        n //= 128
    bytes[-1] += 128
    return pack('%dB' % len(bytes), *bytes)


def encode(numbers):
    bytestream = []
    for n in numbers:
        bytes = vb_encode_number(n)
        bytestream.append(bytes)
    return b"".join(bytestream)


def decode(bytestream):
    numbers = []
    n = 0
    bytestream = unpack('%dB' % len(bytestream), bytestream)
    for i in range(len(bytestream)):
        if bytestream[i] < 128:
            n = 128 * n + bytestream[i]
        else:
            n = 128 * n + (bytestream[i] - 128)
            numbers.append(n)
            n = 0
    return numbers
