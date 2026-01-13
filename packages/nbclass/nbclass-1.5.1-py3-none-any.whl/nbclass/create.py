# -*- coding: utf-8 -*-
"""
@ Created on 2024-09-04 15:54
---------
@summary: 
---------
@author: XiaoBai
"""
import datetime
import json
import pprint
import re
from typing import Any, Union, Dict, List, Tuple

from nbclass.log import logger

_regexs = {}


def get_info(html, regexs, allow_repeat=True, fetch_one=False, split=None):
    regexs = isinstance(regexs, str) and [regexs] or regexs

    infos = []
    for regex in regexs:
        if regex == "":
            continue

        if regex not in _regexs.keys():
            _regexs[regex] = re.compile(regex, re.S)

        if fetch_one:
            infos = _regexs[regex].search(html)
            if infos:
                infos = infos.groups()
            else:
                continue
        else:
            infos = _regexs[regex].findall(str(html))

        if len(infos) > 0:
            # print(regex)
            break

    if fetch_one:
        infos = infos if infos else ("",)
        return infos if len(infos) > 1 else infos[0]
    else:
        infos = allow_repeat and infos or sorted(set(infos), key=infos.index)
        infos = split.join(infos) if split else infos
        return infos


def get_json(json_str):
    """
    @summary: 取json对象
    ---------
    @param json_str: json格式的字符串
    ---------
    @result: 返回json对象
    """

    try:
        return json.loads(json_str) if json_str else {}
    except Exception as e1:
        try:
            json_str = json_str.strip()
            json_str = json_str.replace("'", '"')
            keys = get_info(json_str, r"(\w+):")
            for key in keys:
                json_str = json_str.replace(key, '"%s"' % key)

            return json.loads(json_str) if json_str else {}

        except Exception as e2:
            logger.error(
                """
                e1: %s
                format json_str: %s
                e2: %s
                """
                % (e1, json_str, e2)
            )

        return {}


def dumps_json(data, indent: Any = 4, sort_keys=False):
    """
    @summary: 格式化json 用于打印
    ---------
    @param data: json格式的字符串或json对象
    @param indent:
    @param sort_keys:
    ---------
    @result: 格式化后的字符串
    """
    try:
        if isinstance(data, str):
            data = get_json(data)

        data = json.dumps(
            data,
            ensure_ascii=False,
            indent=indent,
            skipkeys=True,
            sort_keys=sort_keys,
            default=str,
        )

    except Exception as e:
        logger.debug(e)
        data = pprint.pformat(data)

    return data


def format_sql_value(value):
    if isinstance(value, str):
        value = value.strip()

    elif isinstance(value, (list, dict)):
        value = dumps_json(value, indent=None)

    elif isinstance(value, (datetime.date, datetime.time)):
        value = str(value)

    elif isinstance(value, bool):
        value = int(value)

    return value


def key2underline(key: str, strict=True):
    """
    >>> key2underline("HelloWord")
    'hello_word'
    >>> key2underline("SHData", strict=True)
    's_h_data'
    >>> key2underline("SHData", strict=False)
    'sh_data'
    >>> key2underline("SHDataHi", strict=False)
    'sh_data_hi'
    >>> key2underline("SHDataHi", strict=True)
    's_h_data_hi'
    >>> key2underline("dataHi", strict=True)
    'data_hi'
    """
    regex = "[A-Z]*" if not strict else "[A-Z]"
    capitals = re.findall(regex, key)

    if capitals:
        for capital in capitals:
            if not capital:
                continue
            if key.startswith(capital):
                if len(capital) > 1:
                    key = key.replace(
                        capital, capital[:-1].lower() + "_" + capital[-1].lower(), 1
                    )
                else:
                    key = key.replace(capital, capital.lower(), 1)
            else:
                if len(capital) > 1:
                    key = key.replace(capital, "_" + capital.lower() + "_", 1)
                else:
                    key = key.replace(capital, "_" + capital.lower(), 1)

    return key.strip("_")


def list2str(datas):
    """
    列表转字符串
    :param datas: [1, 2]
    :return: (1, 2)
    """
    data_str = str(tuple(datas))
    data_str = re.sub(r",\)$", ")", data_str)
    return data_str


def make_batch_sql(
        table: str, datas: dict, auto_update=False, update_columns=(), update_columns_value=()
) -> Union[Tuple[str, list], None]:
    """
    @summary: 生产批量的sql
    ---------
    @param table:
    @param datas: 表数据 [{...}]
    @param auto_update: 使用的是replace into， 为完全覆盖已存在的数据
    @param update_columns: 需要更新的列 默认全部，当指定值时，auto_update设置无效，当duplicate key冲突时更新指定的列
    @param update_columns_value: 需要更新的列的值 默认为datas里边对应的值, 注意 如果值为字符串类型 需要主动加单引号， 如 update_columns_value=("'test'",)
    ---------
    @result:
    """
    if not datas:
        return

    keys = list(set([key for data in datas for key in data]))
    values_placeholder = ["%s"] * len(keys)

    values = []
    for data in datas:
        value = []
        for key in keys:
            current_data = data.get(key)
            current_data = format_sql_value(current_data)

            value.append(current_data)

        values.append(value)

    keys = ["`{}`".format(key) for key in keys]
    keys = list2str(keys).replace("'", "")

    values_placeholder = list2str(values_placeholder).replace("'", "")

    if update_columns:
        if not isinstance(update_columns, (tuple, list)):
            update_columns = [update_columns]
        if update_columns_value:
            update_columns_ = ", ".join(
                [
                    "`{key}`={value}".format(key=key, value=value)
                    for key, value in zip(update_columns, update_columns_value)
                ]
            )
        else:
            update_columns_ = ", ".join(
                ["`{key}`=values(`{key}`)".format(key=key) for key in update_columns]
            )
        sql = ("insert into `{table}` {keys} values {values_placeholder} "
               "on duplicate key update {update_columns}").format(
            table=table,
            keys=keys,
            values_placeholder=values_placeholder,
            update_columns=update_columns_,
        )
    elif auto_update:
        sql = "replace into `{table}` {keys} values {values_placeholder}".format(
            table=table, keys=keys, values_placeholder=values_placeholder
        )
    else:
        sql = "insert ignore into `{table}` {keys} values {values_placeholder}".format(
            table=table, keys=keys, values_placeholder=values_placeholder
        )

    return sql, values


def make_insert_sql(
        table: str, data: dict, auto_update=False, update_columns=(), insert_ignore=False
):
    """
    @summary: 适用于mysql， oracle数据库时间需要to_date 处理（TODO）
    ---------
    @param table:
    @param data: 表数据 json格式
    @param auto_update: 使用的是replace into， 为完全覆盖已存在的数据
    @param update_columns: 需要更新的列 默认全部，当指定值时，auto_update设置无效，当duplicate key冲突时更新指定的列
    @param insert_ignore: 数据存在忽略
    ---------
    @result:
    """

    keys = ["`{}`".format(key) for key in data.keys()]
    keys = list2str(keys).replace("'", "")

    values = [format_sql_value(value) for value in data.values()]
    values = list2str(values)

    if update_columns:
        if not isinstance(update_columns, (tuple, list)):
            update_columns = [update_columns]
        update_columns_ = ", ".join(
            ["{key}=values({key})".format(key=key) for key in update_columns]
        )
        sql = (
                "insert%s into `{table}` {keys} values {values} on duplicate key update %s"
                % (" ignore" if insert_ignore else "", update_columns_)
        )

    elif auto_update:
        sql = "replace into `{table}` {keys} values {values}"
    else:
        sql = "insert%s into `{table}` {keys} values {values}" % (
            " ignore" if insert_ignore else ""
        )

    sql = sql.format(table=table, keys=keys, values=values).replace("None", "null")
    return sql


def make_update_sql(table: str, data: dict, condition: str):
    """
    @summary: 适用于mysql， oracle数据库时间需要to_date 处理（TODO）
    ---------
    @param table:
    @param data: 表数据 json格式
    @param condition: where 条件
    ---------
    @result:
    """
    key_values = []

    for key, value in data.items():
        value = format_sql_value(value)
        if isinstance(value, str):
            key_values.append("`{}`={}".format(key, repr(value)))
        elif value is None:
            key_values.append("`{}`={}".format(key, "null"))
        else:
            key_values.append("`{}`={}".format(key, value))

    key_values = ", ".join(key_values)

    sql = f"update `{table}` set {key_values} where {condition}"
    return sql


def make_query_sql(table: str, keys: Union[List[str], Dict[str, str]], condition: str = '1=1'):
    """
    @summary: 适用于mysql
    ---------
    @param table: 表名称
    @param keys: 查询的字段
            如果传入的是列表:
                ['id', 'name', 'create_time', 'update_time'] ->
                select `id`, `name`, `create_time`, `update_time`
            如果传入的是字典:
                {'name': 'alias', 'createTime': 'create_time'} ->
                select `name` as `alias`, `createTime` as `create_time`

    @param condition: where 条件
    ---------
    @result:
    """

    if isinstance(keys, list):
        key_values = ["`{}`".format(key) for key in keys]
    elif isinstance(keys, dict):
        key_values = []
        for key, value in keys.items():
            value = format_sql_value(value)
            key_values.append("`{}` as `{}`".format(key, str(value)))
    else:
        raise ValueError('keys must be a')

    key_values = ','.join(key_values)
    sql = f'''select {key_values} from `{table}` where {condition}'''
    return sql
