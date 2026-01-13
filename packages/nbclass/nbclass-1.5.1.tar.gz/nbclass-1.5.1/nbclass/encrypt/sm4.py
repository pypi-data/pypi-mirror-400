# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-11 13:52
---------
@summary: 
---------
@author: XiaoBai
"""
import base64
import copy
from functools import cached_property

from .func import xor, rotl, get_uint32_be, put_uint32_be, \
    bytes_to_list, list_to_bytes, pkcs7_padding, pkcs7_unpadding, zero_padding, zero_unpadding
from ..typeshed import StrBytes

# Expanded SM4 box table
SM4_BOXES_TABLE = [
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c,
    0x05, 0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86,
    0x06, 0x99, 0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed,
    0xcf, 0xac, 0x62, 0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa,
    0x75, 0x8f, 0x3f, 0xa6, 0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c,
    0x19, 0xe6, 0x85, 0x4f, 0xa8, 0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb,
    0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35, 0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25,
    0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87, 0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52,
    0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e, 0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38,
    0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1, 0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34,
    0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3, 0x1d, 0xf6, 0xe2, 0x2e, 0x82,
    0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f, 0xd5, 0xdb, 0x37, 0x45,
    0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51, 0x8d, 0x1b, 0xaf,
    0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8, 0x0a, 0xc1,
    0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0, 0x89,
    0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39,
    0x48,
]

# System parameter
SM4_FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

# fixed parameter
SM4_CK = [
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
]

SM4_ENCRYPT = 0
SM4_DECRYPT = 1

PKCS7 = 0
ZERO = 1


class EncodeType:
    HEX = 1
    B64 = 2
    STR = 3
    BYTES = 4


class Response:
    def __init__(self, data: bytes):
        self._data = data

    def hex(self) -> str:
        return self._data.hex()

    def b64(self) -> str:
        return base64.b64encode(self._data).decode()

    def str(self) -> str:
        return self._data.decode()

    def __str__(self):
        return self._data.decode()

    def bytes(self) -> bytes:
        return self._data


class CryptSM4(object):

    def __init__(self, secret_key: StrBytes, padding_mode: int = PKCS7):
        """
        :param secret_key: 密钥key
        :param padding_mode: 填错方式
        """
        self.secret_key = bytes.fromhex(secret_key) if isinstance(secret_key, str) else secret_key
        self.padding_mode = padding_mode

    @classmethod
    def _round_key(cls, ka):
        b = [0, 0, 0, 0]
        a = put_uint32_be(ka)
        b[0] = SM4_BOXES_TABLE[a[0]]
        b[1] = SM4_BOXES_TABLE[a[1]]
        b[2] = SM4_BOXES_TABLE[a[2]]
        b[3] = SM4_BOXES_TABLE[a[3]]
        bb = get_uint32_be(b[0:4])
        rk = bb ^ (rotl(bb, 13)) ^ (rotl(bb, 23))
        return rk

    @classmethod
    def _f(cls, x0, x1, x2, x3, rk):
        def _sm4_l_t(ka):
            b = [0, 0, 0, 0]
            a = put_uint32_be(ka)
            b[0] = SM4_BOXES_TABLE[a[0]]
            b[1] = SM4_BOXES_TABLE[a[1]]
            b[2] = SM4_BOXES_TABLE[a[2]]
            b[3] = SM4_BOXES_TABLE[a[3]]
            bb = get_uint32_be(b[0:4])
            c = bb ^ (
                rotl(bb, 2)) ^ (
                    rotl(bb, 10)) ^ (
                    rotl(bb, 18)) ^ (
                    rotl(bb, 24))
            return c

        return x0 ^ _sm4_l_t(x1 ^ x2 ^ x3 ^ rk)

    @cached_property
    def _encry_sk(self):
        sk = [0] * 32
        key = bytes_to_list(self.secret_key)
        MK = [0, 0, 0, 0]
        k = [0] * 36
        MK[0] = get_uint32_be(key[0:4])
        MK[1] = get_uint32_be(key[4:8])
        MK[2] = get_uint32_be(key[8:12])
        MK[3] = get_uint32_be(key[12:16])
        k[0:4] = xor(MK[0:4], SM4_FK[0:4])
        for i in range(32):
            k[i + 4] = k[i] ^ (
                self._round_key(k[i + 1] ^ k[i + 2] ^ k[i + 3] ^ SM4_CK[i]))
            sk[i] = k[i + 4]

        return sk

    @cached_property
    def _decry_sk(self):
        sk = self._encry_sk
        for idx in range(16):
            t = sk[idx]
            sk[idx] = sk[31 - idx]
            sk[31 - idx] = t
        return sk

    def one_round(self, sk, in_put):
        out_put = []
        buf = [0] * 36
        buf[0] = get_uint32_be(in_put[0:4])
        buf[1] = get_uint32_be(in_put[4:8])
        buf[2] = get_uint32_be(in_put[8:12])
        buf[3] = get_uint32_be(in_put[12:16])
        for idx in range(32):
            buf[idx + 4] = self._f(
                buf[idx],
                buf[idx + 1],
                buf[idx + 2],
                buf[idx + 3],
                sk[idx]
            )

        out_put += put_uint32_be(buf[35])
        out_put += put_uint32_be(buf[34])
        out_put += put_uint32_be(buf[33])
        out_put += put_uint32_be(buf[32])
        return out_put

    def _loop(self, input_data, sk) -> list:
        length = len(input_data)
        i = 0
        output_data = []
        while length > 0:
            output_data += self.one_round(sk, input_data[i:i + 16])
            i += 16
            length -= 16

        return output_data

    @staticmethod
    def _transform_input(data, typ) -> bytes:
        if typ == EncodeType.HEX:
            data = bytes.fromhex(data)
        elif typ == EncodeType.B64:
            data = base64.b64decode(data)
        elif typ == EncodeType.STR:
            data = data.encode()
        return data

    def encrypt_ecb(self, msg: StrBytes) -> Response:
        # SM4-ECB block encryption/decryption
        message = bytes_to_list(msg.encode() if isinstance(msg, str) else msg)
        if self.padding_mode == PKCS7:
            message = pkcs7_padding(message)

        elif self.padding_mode == ZERO:
            message = zero_padding(message)

        output_data = self._loop(message, self._encry_sk)
        return Response(list_to_bytes(output_data))

    def decrypt_ecb(self, msg: StrBytes, input_type: EncodeType) -> str:
        # SM4-ECB
        message = bytes_to_list(self._transform_input(msg, input_type))
        output_data = self._loop(message, self._decry_sk)
        if self.padding_mode == PKCS7:
            return list_to_bytes(pkcs7_unpadding(output_data)).decode()

        elif self.padding_mode == ZERO:
            return list_to_bytes(zero_unpadding(output_data)).decode()

        return list_to_bytes(output_data).decode()

    def encrypt_cbc(self, iv: StrBytes, msg: StrBytes) -> Response:
        # SM4-CBC buffer encryption/decryption
        i = 0
        output_data = []
        tmp_input = [0] * 16
        iv = bytes_to_list(bytes.fromhex(iv) if isinstance(iv, str) else iv)

        message = pkcs7_padding(bytes_to_list(msg.encode() if isinstance(msg, str) else msg))
        length = len(message)

        while length > 0:
            tmp_input[0:16] = xor(message[i:i + 16], iv[0:16])
            output_data += self.one_round(self._encry_sk, tmp_input[0:16])
            iv = copy.deepcopy(output_data[i:i + 16])
            i += 16
            length -= 16

        return Response(list_to_bytes(output_data))

    def decrypt_cbc(self, iv, msg: StrBytes, input_type: EncodeType) -> str:
        # SM4-CBC buffer encryption/decryption
        i = 0
        output_data = []
        iv = bytes_to_list(bytes.fromhex(iv) if isinstance(iv, str) else iv)
        message = self._transform_input(msg, input_type)
        length = len(message)

        while length > 0:
            output_data += self.one_round(self._decry_sk, message[i:i + 16])
            output_data[i:i + 16] = xor(output_data[i:i + 16], iv[0:16])
            iv = copy.deepcopy(message[i:i + 16])
            i += 16
            length -= 16

        return list_to_bytes(pkcs7_unpadding(output_data)).decode()
