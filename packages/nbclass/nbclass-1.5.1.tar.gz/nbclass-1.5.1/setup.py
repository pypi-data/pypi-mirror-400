# -*- coding: utf-8 -*-
"""
@ Created on 2024-09-04 17:00
---------
@summary: 
---------
@author: XiaoBai
"""
from sys import version_info

import setuptools

if version_info < (3, 6, 0):
    raise SystemExit("Sorry! nbclass requires python 3.6.0 or later.")

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

packages = setuptools.find_packages()
packages.extend(
    [
        "nbclass",
    ]
)

requires = [
    "DBUtils>=3.0.3",
    "loguru>=0.6.0",
    "openpyxl>=3.1.2",
    "prettytable>=3.11.0",
    "pycryptodome>=3.17",
    "PyExecJS>=1.5.1",
    "pymongo>=4.7.2",
    "PyMySQL>=1.0.2",
    "redis>=3.5.3",
    "tqdm>=4.65.0",
    "xlrd>=2.0.1",
    "xlutils>=2.0.0",
    "xlwt>=1.3.0",
    "shapely>=2.0.1",
]

render_requires = [
]

all_requires = [
                   "redis-py-cluster>=2.1.0"
               ] + render_requires

setuptools.setup(
    name="nbclass",
    version="1.5.1",
    author="XiaoBai",
    license="MIT",
    author_email="1808269437@qq.com",
    python_requires=">=3.6",
    description="nbclass工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requires,
    extras_require={"all": all_requires, "render": render_requires},
    # entry_points={"console_scripts": [""]},
    # url="",
    packages=packages,
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)
