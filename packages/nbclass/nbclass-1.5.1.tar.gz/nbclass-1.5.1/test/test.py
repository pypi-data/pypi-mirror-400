# -*- coding: utf-8 -*-
"""
@ Created on 2024-09-04 15:48
---------
@summary: 
---------
@author: XiaoBai
"""

import pyotp

from nbclass import tools

# 生成pypi登录的第二重身份验证应用程序代码
key = ''
totp = pyotp.TOTP(key)
print(totp.now())
"""
打包 python setup.py sdist bdist_wheel
发布 twine upload dist/* --repository nbclass
发布 twine upload dist/* --repository pygeocoding
"""

