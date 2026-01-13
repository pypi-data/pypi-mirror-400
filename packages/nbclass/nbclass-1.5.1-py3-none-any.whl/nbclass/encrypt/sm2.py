# -*- coding: utf-8 -*-
"""
@ Created on 2025-06-10 18:10
---------
@summary: 
---------
@author: XiaoBai
"""
import binascii
import secrets
from math import ceil

from Cryptodome.Util.asn1 import DerSequence, DerInteger

from nbclass.encrypt import sm3, func
from nbclass.typeshed import StrBytes

SM2_PRIME = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
SM2_A = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
SM2_B = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
SM2_BASE_POINT = (
    0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7,
    0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
)


class DefaultECDLP:
    n = 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123'
    p = 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF'
    g = ('32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7'
         'bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0')
    a = 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC'
    b = '28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93'


class SM2Core:
    def __init__(self, ecc_table: DefaultECDLP):
        self.ecc_table = ecc_table
        self.para_len = 64 or len(ecc_table.n)
        self.ecc_a3 = (int(ecc_table.a, base=16) + 3) % int(ecc_table.p, base=16)

    def _kg(self, k, Point):  # kP运算
        Point = '%s%s' % (Point, '1')
        mask_str = '8'
        for i in range(self.para_len - 1):
            mask_str += '0'
        mask = int(mask_str, 16)
        Temp = Point
        flag = False
        for n in range(self.para_len * 4):
            if flag:
                Temp = self._double_point(Temp)
            if (k & mask) != 0:
                if flag:
                    Temp = self._add_point(Temp, Point)
                else:
                    flag = True
                    Temp = Point
            k = k << 1
        return self._convert_jacb_to_nor(Temp)

    @staticmethod
    def _default_rnd_fn(k: int) -> int:
        return secrets.randbits(k)

    def _randint(self, a: int, b: int) -> int:
        bit_length = b.bit_length()
        while True:
            n = self._default_rnd_fn(bit_length)
            if n < a or n > b:
                continue
            return n

    def _double_point(self, Point):  # 倍点
        length = len(Point)
        len_2 = 2 * self.para_len
        if length < self.para_len * 2:
            return None
        else:
            x1 = int(Point[0:self.para_len], 16)
            y1 = int(Point[self.para_len:len_2], 16)
            if length == len_2:
                z1 = 1
            else:
                z1 = int(Point[len_2:], 16)

            T6 = (z1 * z1) % int(self.ecc_table.p, base=16)
            T2 = (y1 * y1) % int(self.ecc_table.p, base=16)
            T3 = (x1 + T6) % int(self.ecc_table.p, base=16)
            T4 = (x1 - T6) % int(self.ecc_table.p, base=16)
            T1 = (T3 * T4) % int(self.ecc_table.p, base=16)
            T3 = (y1 * z1) % int(self.ecc_table.p, base=16)
            T4 = (T2 * 8) % int(self.ecc_table.p, base=16)
            T5 = (x1 * T4) % int(self.ecc_table.p, base=16)
            T1 = (T1 * 3) % int(self.ecc_table.p, base=16)
            T6 = (T6 * T6) % int(self.ecc_table.p, base=16)
            T6 = (self.ecc_a3 * T6) % int(self.ecc_table.p, base=16)
            T1 = (T1 + T6) % int(self.ecc_table.p, base=16)
            z3 = (T3 + T3) % int(self.ecc_table.p, base=16)
            T3 = (T1 * T1) % int(self.ecc_table.p, base=16)
            T2 = (T2 * T4) % int(self.ecc_table.p, base=16)
            x3 = (T3 - T5) % int(self.ecc_table.p, base=16)

            if (T5 % 2) == 1:
                T4 = (T5 + ((T5 + int(self.ecc_table.p, base=16)) >> 1) - T3) % int(
                    self.ecc_table.p, base=16)
            else:
                T4 = (T5 + (T5 >> 1) - T3) % int(self.ecc_table.p, base=16)

            T1 = (T1 * T4) % int(self.ecc_table.p, base=16)
            y3 = (T1 - T2) % int(self.ecc_table.p, base=16)

            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (x3, y3, z3)

    def _add_point(self, P1, P2):
        """ 点加函数，P2点为仿射坐标即z=1，P1为Jacobian加重射影坐标 """
        len_2 = 2 * self.para_len
        l1 = len(P1)
        l2 = len(P2)
        if (l1 < len_2) or (l2 < len_2):
            return None
        else:
            X1 = int(P1[0:self.para_len], 16)
            Y1 = int(P1[self.para_len:len_2], 16)
            if l1 == len_2:
                Z1 = 1
            else:
                Z1 = int(P1[len_2:], 16)
            x2 = int(P2[0:self.para_len], 16)
            y2 = int(P2[self.para_len:len_2], 16)

            T1 = (Z1 * Z1) % int(self.ecc_table.p, base=16)
            T2 = (y2 * Z1) % int(self.ecc_table.p, base=16)
            T3 = (x2 * T1) % int(self.ecc_table.p, base=16)
            T1 = (T1 * T2) % int(self.ecc_table.p, base=16)
            T2 = (T3 - X1) % int(self.ecc_table.p, base=16)
            T3 = (T3 + X1) % int(self.ecc_table.p, base=16)
            T4 = (T2 * T2) % int(self.ecc_table.p, base=16)
            T1 = (T1 - Y1) % int(self.ecc_table.p, base=16)
            Z3 = (Z1 * T2) % int(self.ecc_table.p, base=16)
            T2 = (T2 * T4) % int(self.ecc_table.p, base=16)
            T3 = (T3 * T4) % int(self.ecc_table.p, base=16)
            T5 = (T1 * T1) % int(self.ecc_table.p, base=16)
            T4 = (X1 * T4) % int(self.ecc_table.p, base=16)
            X3 = (T5 - T3) % int(self.ecc_table.p, base=16)
            T2 = (Y1 * T2) % int(self.ecc_table.p, base=16)
            T3 = (T4 - X3) % int(self.ecc_table.p, base=16)
            T1 = (T1 * T3) % int(self.ecc_table.p, base=16)
            Y3 = (T1 - T2) % int(self.ecc_table.p, base=16)

            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (X3, Y3, Z3)

    def _convert_jacb_to_nor(self, Point):  # Jacobian加重射影坐标转换成仿射坐标
        len_2 = 2 * self.para_len
        x = int(Point[0:self.para_len], 16)
        y = int(Point[self.para_len:len_2], 16)
        z = int(Point[len_2:], 16)
        z_inv = pow(
            z, int(self.ecc_table.p, base=16) - 2, int(self.ecc_table.p, base=16))
        z_invSquar = (z_inv * z_inv) % int(self.ecc_table.p, base=16)
        z_invQube = (z_invSquar * z_inv) % int(self.ecc_table.p, base=16)
        x_new = (x * z_invSquar) % int(self.ecc_table.p, base=16)
        y_new = (y * z_invQube) % int(self.ecc_table.p, base=16)
        z_new = (z * z_inv) % int(self.ecc_table.p, base=16)
        if z_new == 1:
            form = '%%0%dx' % self.para_len
            form = form * 2
            return form % (x_new, y_new)
        else:
            return None

    def _point_multiply(self, k, point):
        """
        椭圆曲线点乘法：计算 k * point
        :param k: 整数，私钥
        :param point: 椭圆曲线上的点 (x, y)
        :return: 椭圆曲线上的点 (x, y)
        """
        result = None
        addend = point

        while k:
            if k & 1:
                if result is None:
                    result = addend
                else:
                    result = self._point_add(result, addend)
            addend = self._point_add(addend, addend)
            k >>= 1

        return result

    @staticmethod
    def _point_add(p1, p2):
        """
        椭圆曲线点加法：计算 p1 + p2
        :param p1: 椭圆曲线上的点 (x1, y1)
        :param p2: 椭圆曲线上的点 (x2, y2)
        :return: 椭圆曲线上的点 (x, y)
        """
        if p1 is None:
            return p2
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2 and y1 != y2:
            return None

        if x1 == x2:
            m = (3 * x1 * x1 + SM2_A) * pow(2 * y1, SM2_PRIME - 2, SM2_PRIME)
        else:
            m = (y2 - y1) * pow(x2 - x1, SM2_PRIME - 2, SM2_PRIME)

        x3 = (m * m - x1 - x2) % SM2_PRIME
        y3 = (m * (x1 - x3) - y1) % SM2_PRIME

        return x3, y3

    @staticmethod
    def _sm3_kdf(z, length):
        """
        :param z: 16进制表示的比特串（str）
        :param length: 密钥长度（单位byte）
        :return:
        """
        length = int(length)
        ct = 0x00000001
        r_cnt = ceil(length / 32)
        zin = [i for i in bytes.fromhex(z.decode('utf8'))]
        ha = ""
        for i in range(r_cnt):
            msg = zin + [i for i in binascii.a2b_hex(('%08x' % ct).encode('utf8'))]
            ha = ha + sm3.sm3_hash(msg)
            ct += 1
        return ha[0: length * 2]


class CryptSM2(SM2Core):
    def __init__(self, private_key: str = None, public_key: str = None, ecc_table=DefaultECDLP, mode=0, asn1=False):
        super().__init__(ecc_table)
        # 密钥处理
        if private_key is None and public_key is None:
            self.private_key, self.public_key = self.generate_keypair()
        elif private_key is not None:
            self.private_key = private_key
            if public_key is None:
                self.public_key = self.generate_public_key(private_key)
            else:
                self.public_key = public_key
        else:
            self.private_key = ""
            self.public_key = public_key

        # 移除公钥前缀（如果存在）
        if self.public_key.startswith("04"):
            self.public_key = self.public_key[2:]

        assert len(self.private_key) == 64, "私钥长度必须为64位"
        assert len(self.public_key) == 128, "公钥长度必须为128位"
        assert mode in (0, 1), '模式必须是其中之一 (0, 1)'

        self.mode = mode
        self.asn1 = asn1

    def generate_public_key(self, private_key: str):
        """
        从 SM2 私钥生成公钥。
        :param private_key字符串形式的 SM2 私钥
        :return: 十六进制字符串形式的 SM2 公钥
        """
        # 将私钥从十六进制字符串转换为整数
        private_key = int(private_key, 16)

        # 计算公钥：公钥 = 私钥 * 基点
        public_key = self._point_multiply(private_key, SM2_BASE_POINT)

        # 将公钥转换为十六进制字符串
        public_key_hex = f"04{public_key[0]:064x}{public_key[1]:064x}"
        return public_key_hex

    def generate_private_key(self) -> int:
        sk = self._randint(1, int(self.ecc_table.p, 16) - 2)
        return sk

    def generate_keypair(self):
        """ 生成密钥对 """
        sk = self.generate_private_key()
        sk = func.int_to_bytes(sk).hex()

        return sk, self.generate_public_key(sk)

    @staticmethod
    def str_to_hex(hex_str):
        """
        字符串转hex
        :param hex_str: 字符串
        :return: hex
        """
        hex_data = hex_str.encode('utf-8')
        return hex_data.hex()

    def get_point(self) -> dict:
        """ 获取椭圆曲线点 """
        k = self.generate_private_key()
        x1 = self._point_multiply(k, SM2_BASE_POINT)[0]

        return {
            'k': k,
            'x1': x1
        }

    def sign(self, data: StrBytes, K: str = None) -> str:
        """
        :param data: data消息
        :param K: K随机数
        :return:
        """
        if isinstance(data, str):
            data = data.encode()

        E = data.hex()  # 消息转化为16进制字符串
        e = int(E, 16)

        k = int(K or func.random_hex(self.para_len), 16)
        d = int(self.private_key, 16)
        nn = int(self.ecc_table.n, 16)
        P1 = self._kg(k, self.ecc_table.g)

        x = int(P1[0:self.para_len], 16)
        R = ((e + x) % nn)
        if R == 0 or R + k == self.ecc_table.n:
            return ''
        d_1 = pow(d + 1, nn - 2, nn)
        S = (d_1 * (k + R) - R) % nn
        if S == 0:
            return ''
        elif self.asn1:
            return DerSequence([DerInteger(R), DerInteger(S)]).encode().hex()
        else:
            return '%064x%064x' % (R, S)

    def verify(self, sign, data, is_hex=False) -> bool:
        # 验签函数
        if isinstance(data, str):
            data = data.encode() if is_hex is False else bytes.fromhex(data)
        if self.asn1:
            unhex_sign = binascii.unhexlify(sign.encode())
            seq_der = DerSequence()
            origin_sign = seq_der.decode(unhex_sign)
            r = origin_sign[0]
            s = origin_sign[1]
        else:
            r = int(sign[0:self.para_len], 16)
            s = int(sign[self.para_len:2 * self.para_len], 16)
        e = int(data.hex(), 16)
        t = (r + s) % int(self.ecc_table.n, base=16)
        if t == 0:
            return False

        P1 = self._kg(s, self.ecc_table.g)
        P2 = self._kg(t, self.public_key)

        if P1 == P2:
            P1 = '%s%s' % (P1, 1)
            P1 = self._double_point(P1)
        else:
            P1 = '%s%s' % (P1, 1)
            P1 = self._add_point(P1, P2)
            P1 = self._convert_jacb_to_nor(P1)

        x = int(P1[0:self.para_len], 16)
        return r == ((e + x) % int(self.ecc_table.n, base=16))

    def signature(self, msg: StrBytes, point: dict = None, **options) -> str:
        """

        :param msg:
        :param point: 椭圆曲线点
        :param options: userId: 用户Id, hash: 是否哈希, asn1
        :return:
        """
        user_id = options.get('userId', '1234567812345678')
        use_hash = options.get('hash', True)
        asn1 = options.get('asn1', None)
        asn1 = self.asn1 if asn1 is None else asn1
        if use_hash:
            hash_hex = self.get_hash(msg, user_id)
        else:
            hash_hex = self.str_to_hex(msg) if isinstance(msg, str) else msg.hex()

        da = int(self.private_key, 16)
        e = int(hash_hex, 16)
        n = int(self.ecc_table.n, 16)

        while True:
            while True:
                if not point:
                    point = self.get_point()
                k = point['k']
                r = (e + point['x1']) % n
                if r != 0 and (r + k) % n != 0:
                    break
            s = pow(da + 1, -1, n) * (k - r * da) % n
            if s != 0:
                break
        if asn1:
            return DerSequence([DerInteger(r), DerInteger(s)]).encode().hex()

        return hex(r)[2:] + hex(s)[2:]

    def verify_signature(self, msg, sign, **options) -> bool:
        user_id = options.get('userId', '1234567812345678')  # 默认用户ID
        use_hash = options.get('hash', True)
        asn1 = options.get('asn1', None)
        asn1 = self.asn1 if asn1 is None else asn1

        if use_hash:
            hash_hex = self.get_hash(msg, user_id)
        else:
            hash_hex = self.str_to_hex(msg) if isinstance(msg, str) else msg.hex()

        if asn1:
            der_seq = DerSequence()
            der_seq.decode(sign)
            r = der_seq[0]  # 提取 r
            s = der_seq[1]  # 提取 s
        else:
            r = int(sign[:64], 16)
            s = int(sign[64:], 16)

        n = int(self.ecc_table.n, 16)
        e = int(hash_hex, 16)
        t = (r + s) % n  # t = (r + s) mod n

        if t == 0:
            return False
        pa = self._point_multiply(s, SM2_BASE_POINT)
        pb = self._point_multiply(t, (int(self.public_key[:64], 16), int(self.public_key[64:], 16)))
        x1y1 = self._point_add(pa, pb)
        r1 = (e + x1y1[0]) % n
        return r == r1

    def get_hash(self, data: StrBytes, user_id: str = '1234567812345678'):
        data = self.str_to_hex(data) if isinstance(data, str) else data.hex()
        z = '0040' + self.str_to_hex(user_id) + \
            self.ecc_table.a + self.ecc_table.b + self.ecc_table.g + \
            self.public_key
        z = binascii.a2b_hex(z)
        Za = sm3.sm3_hash(func.bytes_to_list(z))
        M_ = (Za + data).encode('utf-8')
        e = sm3.sm3_hash(func.bytes_to_list(binascii.a2b_hex(M_)))
        return e

    def encrypt(self, data: StrBytes):
        # 加密函数
        if isinstance(data, str):
            data = data.encode()

        msg = data.hex()
        k = func.random_hex(self.para_len)
        C1 = self._kg(int(k, 16), self.ecc_table.g)
        xy = self._kg(int(k, 16), self.public_key)
        x2 = xy[0:self.para_len]
        y2 = xy[self.para_len:2 * self.para_len]
        ml = len(msg)
        t = self._sm3_kdf(xy.encode('utf8'), ml / 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % ml
            C2 = form % (int(msg, 16) ^ int(t, 16))
            C3 = sm3.sm3_hash([
                i for i in bytes.fromhex('%s%s%s' % (x2, msg, y2))
            ])
            if self.mode:
                return bytes.fromhex('%s%s%s' % (C1, C3, C2))
            else:
                return bytes.fromhex('%s%s%s' % (C1, C2, C3))

    def decrypt(self, data: StrBytes, is_hex=False):
        """
        解密函数
        :param data:
        :param is_hex: 密文是否为十六进制字符串
        :return:
        """
        if isinstance(data, str):
            data = data.encode() if is_hex is False else bytes.fromhex(data)

        data = data.hex()
        len_2 = 2 * self.para_len
        len_3 = len_2 + 64
        C1 = data[0:len_2]

        if self.mode:
            C2 = data[len_3:]
        else:
            C2 = data[len_2:-64]

        xy = self._kg(int(self.private_key, 16), C1)

        cl = len(C2)
        t = self._sm3_kdf(xy.encode('utf8'), cl / 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % cl
            M = form % (int(C2, 16) ^ int(t, 16))
            return bytes.fromhex(M)
