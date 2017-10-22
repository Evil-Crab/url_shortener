# -*- coding: utf-8 -*-

import random

ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
BASE = len(ALPHABET)


def encode(num, min_len=1):
    encoded = ''
    while num > 0:
        encoded = ALPHABET[num % BASE] + encoded
        num //= BASE

    if encoded == '':
        encoded = ALPHABET[0]

    return encoded.ljust(min_len, ALPHABET[0])


def generate_id():
    random_suffix = random.randrange(BASE**8)

    return encode(random_suffix)


def validate(encoded_string):
    try:
        decode(encoded_string)
        return True
    except ValueError:
        return False


def decode(encoded_string):
    value = 0
    power = 0
    for char in encoded_string[::-1]:
        value += char_value(char) * (BASE ** power)
        power += 1

    return value


def char_value(char):
    try:
        return ALPHABET.index(char)
    except ValueError:
        raise ValueError(f'Invalid character: {char}')
