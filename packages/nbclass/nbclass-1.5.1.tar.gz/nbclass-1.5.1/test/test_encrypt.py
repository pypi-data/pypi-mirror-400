# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-11 13:51
---------
@summary: 
---------
@author: XiaoBai
"""

from nbclass import tools
from nbclass.encrypt import CryptSM2


def test_sha1():
    print(tools.get_sha1('123456'))


class Sm2Test:
    privateKey = "17d7cf5e57b0ca0d5db32409d222888b3bc0a711ac05707d1e0ea1f31d2ab5b1"
    publicKey = ("049312271263f0d43dc145a9bd9c582c5d303f249f483a029798eef6dca21a5ec"
                 "b7cc0855a30a8a506cf2bc6b79ada3f9027db60e9a0e7531b82faf7b731d0f281")

    def __init__(self):
        self.sm2 = CryptSM2(self.privateKey, self.publicKey)

    def test_sign(self):
        msg = 'bf9e57456f0bb709471783fa1aad8a3b7f1bef38'
        sign = self.sm2.sign(msg, '123456789abcdef')
        print(sign)
        verify = self.sm2.verify(sign, msg)
        print(verify)

    def test_signature(self):
        msg = 'bf9e57456f0bb709471783fa1aad8a3b7f1bef38'

        sign = self.sm2.signature(
            msg,
            # point={
            #     'k': 79841127600118094286629057534724738748201916457378844159533364152781336801938,
            #     'x1': 4470216969468172813767138219699284089914153202156248102026802126561098446599
            # },
            hash=True,
            # asn1=True,
            userId='00000003'
        )
        print(sign)

        verify = self.sm2.verify_signature(
            msg,
            sign,
            hash=True,
            # asn1=True,
            userId='00000003'
        )
        print(verify)

    def test_encrypt(self):
        msg = tools.json_dumps({
            "code": 200,
            "msg": "查询成功",
            "total": 231,
            "rows": [
                {
                    "content": "永昌县2024年度生态及地质灾害避险搬迁项目旧宅基地复垦工程 招标公告",
                    "area": None,
                    "projectType": None,
                    "supplementType": None,
                    "informationType": "招标/资审公告",
                    "preType": None,
                    "releaseTime": "2025-07-22 16:43:45",
                    "approvalPassTime": "2025-07-22 16:43:45",
                    "govDepartmentId": "120",
                    "announcementId": 1978,
                    "bidSectionList": None,
                    "shareBidSectionNum": None,
                    "joinBidSectionFlag": "NO",
                    "canJoinBidSectionFlag": "NO",
                    "focusFlag": "NO",
                    "projectId": 1122,
                    "bidSectionIds": "1718",
                    "openBidStatus": "WAIT_OPEN_BID"
                },
                {
                    "content": "兰张三四线高铁建设(金川区段)330kV电力 线路迁改工程(设计施工总承包)第二标段第二次招标公告",
                    "area": None,
                    "projectType": None,
                    "supplementType": None,
                    "informationType": "招标/资审公告",
                    "preType": None,
                    "releaseTime": "2025-07-17 19:43:42",
                    "approvalPassTime": "2025-07-17 19:43:42"
                }
            ]
        })

        ciphertext = self.sm2.encrypt(msg)
        print(ciphertext.hex())
        plaintext = self.sm2.decrypt(ciphertext, is_hex=True)
        print(plaintext)


def test_sm3_hash():
    from nbclass.encrypt.sm3 import sm3_hash
    print(sm3_hash('123456'))


def test_sm4():
    from nbclass.encrypt.sm4 import CryptSM4 as Sm4, EncodeType
    key = '132F8664322CBA13142E21161297AD91'
    data = '123456789'

    s4 = Sm4(key)
    cbc = s4.encrypt_cbc(iv=key, msg=data).hex()
    ecb = s4.encrypt_ecb(msg=data).hex()
    print('cbc加密', cbc)
    print('ecb加密', ecb)

    cbc_d = s4.decrypt_cbc(iv=key, msg=cbc, input_type=EncodeType.HEX)
    ecb_d = s4.decrypt_ecb(msg=ecb, input_type=EncodeType.HEX)
    print('cbc解密', cbc_d)
    print('ecb解密', ecb_d)


if __name__ == '__main__':
    Sm2Test().test_sign()
    # test_sm3_hash()
