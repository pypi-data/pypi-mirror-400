# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-11 18:12
---------
@summary: 
---------
@author: XiaoBai
"""
import base64

from nbclass.typeshed import StrBytes
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def rsa_encrypt(public_key: str, data: str):
    """
    RSA 加密
    :param public_key: Base64编码的公钥字符串
    :param data: 待加密的字符串
    :return:
    """
    public_key_bytes = RSA.import_key(base64.b64decode(public_key))
    rsa = PKCS1_v1_5.new(public_key_bytes)
    encrypt_msg = rsa.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypt_msg).decode()


def rsa_decrypt(private_key: str, data: StrBytes) -> str:
    """
    RSA解密方法，使用PKCS1_v1_5填充模式

    Args:
        private_key: Base64编码的私钥字符串
        data: Base64编码的加密数据

    Returns:
        解密后的原始字符串
    """

    private_key_bytes = base64.b64decode(private_key)
    rsa_private_key = RSA.import_key(private_key_bytes)

    # 创建解密器
    cipher = PKCS1_v1_5.new(rsa_private_key)

    if isinstance(data, str):
        data = base64.b64decode(data)

    decrypted_bytes = cipher.decrypt(data, None)

    if decrypted_bytes is None:
        raise ValueError("解密失败，密钥不匹配或数据损坏")

    return decrypted_bytes.decode('utf-8')

