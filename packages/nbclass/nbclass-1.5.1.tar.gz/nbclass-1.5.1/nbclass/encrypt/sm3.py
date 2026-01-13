# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-11 13:52
---------
@summary: 
---------
@author: XiaoBai
"""
import typing

from nbclass.encrypt.func import rotl

IV = [
    1937774191, 1226093241, 388252375, 3666478592,
    2842636476, 372324522, 3817729613, 2969243214,
]

T_j = [
    2043430169, 2043430169, 2043430169, 2043430169, 2043430169, 2043430169,
    2043430169, 2043430169, 2043430169, 2043430169, 2043430169, 2043430169,
    2043430169, 2043430169, 2043430169, 2043430169, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042
]


def sm3_ff_j(x, y, z, j):
    if 0 <= j < 16:
        return x ^ y ^ z
    elif 16 <= j < 64:
        return (x & y) | (x & z) | (y & z)
    return None


def sm3_gg_j(x, y, z, j):
    if 0 <= j < 16:
        return x ^ y ^ z
    elif 16 <= j < 64:
        # ret = (X | Y) & ((2 ** 32 - 1 - X) | Z)
        return (x & y) | ((~ x) & z)


def sm3_p_0(x):
    return x ^ (rotl(x, 9 % 32)) ^ (rotl(x, 17 % 32))


def sm3_p_1(x):
    return x ^ (rotl(x, 15 % 32)) ^ (rotl(x, 23 % 32))


def sm3_cf(v_i, b_i):
    w = []
    for i in range(16):
        weight = 0x1000000
        data = 0
        for k in range(i * 4, (i + 1) * 4):
            data = data + b_i[k] * weight
            weight = int(weight / 0x100)
        w.append(data)

    for j in range(16, 68):
        w.append(0)
        w[j] = sm3_p_1(w[j - 16] ^ w[j - 9] ^ (rotl(w[j - 3], 15 % 32))) ^ (rotl(w[j - 13], 7 % 32)) ^ w[j - 6]

    w_1 = []
    for j in range(0, 64):
        w_1.append(0)
        w_1[j] = w[j] ^ w[j + 4]

    a, b, c, d, e, f, g, h = v_i

    for j in range(0, 64):
        ss_1 = rotl(
            ((rotl(a, 12 % 32)) +
             e +
             (rotl(T_j[j], j % 32))) & 0xffffffff, 7 % 32
        )
        ss_2 = ss_1 ^ (rotl(a, 12 % 32))
        tt_1 = (sm3_ff_j(a, b, c, j) + d + ss_2 + w_1[j]) & 0xffffffff
        tt_2 = (sm3_gg_j(e, f, g, j) + h + ss_1 + w[j]) & 0xffffffff
        d = c
        c = rotl(b, 9 % 32)
        b = a
        a = tt_1
        h = g
        g = rotl(f, 19 % 32)
        f = e
        e = sm3_p_0(tt_2)

        a, b, c, d, e, f, g, h = map(
            lambda x: x & 0xFFFFFFFF, [a, b, c, d, e, f, g, h])

    v_j = [a, b, c, d, e, f, g, h]
    return [v_j[i] ^ v_i[i] for i in range(8)]


def sm3_hash(msg: typing.Union[str, list]) -> str:
    """
    :param msg: 明文，字符串或字节列表
    :return: SM3哈希值（十六进制字符串）
    """
    if isinstance(msg, str):
        msg = list(msg.encode())

    msg_len = len(msg)
    msg.append(0x80)

    # 计算填充后长度，使长度对64取模为56
    padding_len = (56 - (msg_len + 1) % 64) % 64
    msg.extend([0x00] * padding_len)

    # 消息长度（bit）用8字节小端存储
    bit_len = msg_len * 8
    for i in range(8):
        msg.append((bit_len >> (8 * (7 - i))) & 0xFF)

    # 分组处理，每组64字节
    group_count = len(msg) // 64
    B = [msg[i * 64:(i + 1) * 64] for i in range(group_count)]

    V = [IV]
    for i in range(group_count):
        V.append(sm3_cf(V[i], B[i]))

    result = ''.join(f'{x:08x}' for x in V[-1])
    return result
