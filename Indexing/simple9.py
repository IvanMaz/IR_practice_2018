# -*- coding: utf-8 -*-
from struct import pack, unpack

n_nums = [28, 14, 9, 7, 5, 4, 3, 2, 1]
thresholds = [2**k - 1 for k in n_nums[::-1]]
codes = [0x90000000, 0x80000000, 0x70000000, 0x60000000,
         0x50000000, 0x40000000, 0x30000000, 0x20000000, 0x10000000]
shifts = [1, 2, 3, 4, 5, 6, 9, 14, 28]


def encode(numbers):
    length = len(numbers)
    encoded = 0
    result = []
    while encoded < length:
        for idx in range(len(n_nums)):
            if encoded + n_nums[idx] <= length and max(numbers[encoded:encoded+n_nums[idx]]) <= thresholds[idx]:
                encoded_number = 0
                for i in range(n_nums[idx]):
                    encoded_number |= (numbers[encoded+i] << (shifts[idx]*i))
                encoded_number |= codes[idx]
                result.append(encoded_number)
                encoded += n_nums[idx]
                break
    return pack('%dL' % len(result), *result)


def decode(bytestream):
    bytestream = unpack('%dL' % (len(bytestream)/8), bytestream)
    numbers = []
    for number in bytestream:
        code = number & 0xf0000000
        payload = number & 0x0fffffff
        idx = codes.index(code)
        for i in range(n_nums[idx]):
            decoded_num = payload & thresholds[idx]
            #numbers.append(int(decoded_num) if decoded_num <= 0x7fffffff else decoded_num)
            numbers.append(decoded_num)
            payload >>= shifts[idx]
    return numbers
