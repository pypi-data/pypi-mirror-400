# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-11 13:54
---------
@summary: 
---------
@author: XiaoBai
"""
import base64
from random import choice


def xor(a, b):
    return list(map(lambda x, y: x ^ y, a, b))


def rotl(x, n):
    return ((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)


def get_uint32_be(key_data):
    return (key_data[0] << 24) | (key_data[1] << 16) | (key_data[2] << 8) | (key_data[3])


def put_uint32_be(n):
    return [((n >> 24) & 0xff), ((n >> 16) & 0xff), ((n >> 8) & 0xff), ((n) & 0xff)]


def pkcs7_padding(data, block=16):
    return data + [(16 - len(data) % block) for _ in range(16 - len(data) % block)]


def zero_padding(data, block=16):
    return data + [0 for _ in range(16 - len(data) % block)]


def pkcs7_unpadding(data):
    return data[:-data[-1]]


def zero_unpadding(data, i=1):
    return data[:-i] if data[-i] == 0 else i + 1


def list_to_bytes(data):
    return b''.join([bytes((i,)) for i in data])


def bytes_to_list(data):
    return [i for i in data]


def int_to_bytes(i: int) -> bytes:
    """Convert integer to minimum number of bytes required to store its value."""

    return i.to_bytes((i.bit_length() + 7) >> 3, "big")


def random_hex(x):
    return ''.join([choice('0123456789abcdef') for _ in range(x)])


def b64encode(ciphertext: bytes) -> str:
    return base64.b64encode(ciphertext).decode()
