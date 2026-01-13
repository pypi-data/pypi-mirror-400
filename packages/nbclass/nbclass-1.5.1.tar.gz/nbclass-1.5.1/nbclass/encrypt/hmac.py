# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-11 18:12
---------
@summary: 
---------
@author: XiaoBai
"""
import hashlib
import hmac

from nbclass.typeshed import StrBytes


def get_md5(*args):
    """
    @summary: 获取唯一的32位md5
    ---------
    @param args: 参与联合去重的值
    ---------
    @result: 7c8684bcbdfcea6697650aa53d7b1405
    """

    m = hashlib.md5()
    for arg in args:
        m.update(str(arg).encode())

    return m.hexdigest()


def get_sha1(*args):
    """
    @summary: 获取唯一的sha1
    ---------
    @result: 356a192b7913b04c54574d18c28d46e6395428ab
    """
    m = hashlib.sha1()
    for arg in args:
        m.update(str(arg).encode())

    return m.hexdigest()


def get_sha256(*args):
    """
    @summary: 获取唯一的64位sha256值
    ---------
    @result:
    """
    m = hashlib.sha256()
    for arg in args:
        m.update(str(arg).encode())

    return m.hexdigest()


def get_sha512(*args):
    """
    @summary: 获取sha512
    ---------
    @result:
    """
    m = hashlib.sha512()
    for arg in args:
        m.update(str(arg).encode())

    return m.hexdigest()


def get_hmac_md5(key: StrBytes, message: StrBytes):
    """
    @summary: 获取hmac_md5
    :param key: 密钥
    :param message: 明文
    ---------
    @result:
    """
    if isinstance(key, str):
        key = key.encode()
    if isinstance(message, str):
        message = message.encode()

    m = hmac.new(key, message, hashlib.md5)

    return m.hexdigest()


def get_hmac_sha1(key: StrBytes, message: StrBytes):
    """
    @summary: 获取hmac_sha1
    :param key: 密钥
    :param message: 明文
    ---------
    @result:
    """
    if isinstance(key, str):
        key = key.encode()
    if isinstance(message, str):
        message = message.encode()

    m = hmac.new(key, message, hashlib.sha1)

    return m.hexdigest()


def get_hmac_sha256(key: StrBytes, message: StrBytes):
    """
    @summary: 获取hmac_sha256
    :param key: 密钥
    :param message: 明文
    ---------
    @result:
    """
    if isinstance(key, str):
        key = key.encode()
    if isinstance(message, str):
        message = message.encode()

    m = hmac.new(key, message, hashlib.sha256)

    return m.hexdigest()


def get_hmac_sha512(key: StrBytes, message: StrBytes):
    """
    @summary: 获取hmac_sha512
    :param key: 密钥
    :param message: 明文
    ---------
    @result:
    """
    if isinstance(key, str):
        key = key.encode()
    if isinstance(message, str):
        message = message.encode()

    m = hmac.new(key, message, hashlib.sha512)

    return m.hexdigest()
