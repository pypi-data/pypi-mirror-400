# -*- coding: utf-8 -*-
"""
@ Created on 2025-05-15 15:37
---------
@summary: 
---------
@author: XiaoBai
"""
import os
import random
from typing import Iterable, List, Optional


from nbclass import tools
from nbclass.db.mysqldb import MysqlDB
from nbclass.db.redis_lock import RedisLock
from nbclass.db.redisdb import RedisDB
from nbclass.log import logger as log
from nbclass.create import make_query_sql
from nbclass.network.user_pool.base_user_pool import UserPoolInterface, TAB_USER_POOL, NormalUser


class NormalUserPool(UserPoolInterface):
    """
    普通用户池，适用于账号成本低且大量的场景
    """

    def __init__(
            self,
            redis_key: str,
            table_userbase: str,
            redis_cli: RedisDB,
            mysql_cli: MysqlDB,
            login_state_key: str = "login_state",
            lock_state_key: str = "lock_state",
            username_key: str = "username",
            password_key: str = "password",
            login_retry_times: int = 1,
            keep_alive: bool = False,
            table_keys: List[str] = None
    ):
        """
        @param redis_key: 项目名
        @param table_userbase: 用户表名
        @param redis_cli: redis数据库链接实例
        @param mysql_cli: MySQL数据库链接实例
        @param login_state_key: 登录状态列名
        @param lock_state_key: 封锁状态列名
        @param username_key: 登陆名列名
        @param password_key: 密码列名
        @param login_retry_times: 登陆失败重试次数
        @param keep_alive: 是否保持常驻，以便user不足时立即补充
        @param table_keys: 其他需要查询的字段列表
        """

        self._tab_user_pool = TAB_USER_POOL.format(
            redis_key=redis_key, user_type="normal"
        )

        self._login_retry_times = login_retry_times
        self._table_userbase = table_userbase
        self._login_state_key = login_state_key
        self._lock_state_key = lock_state_key
        self._username_key = username_key
        self._password_key = password_key
        self._keep_alive = keep_alive
        self._table_keys = table_keys

        self._users_id = []

        self._rdc = redis_cli
        self._mysqldb = mysql_cli

        self._create_userbase()

    def _load_users_id(self):
        self._users_id = self._rdc.hkeys(self._tab_user_pool)
        if self._users_id:
            random.shuffle(self._users_id)

    def _get_user_id(self):
        if not self._users_id:
            self._load_users_id()

        if self._users_id:
            return self._users_id.pop()

    def _create_userbase(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS `{self._table_userbase}` (
              `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
              `{self._username_key}` varchar(50) DEFAULT NULL COMMENT '用户名',
              `{self._password_key}` varchar(255) DEFAULT NULL COMMENT '密码',
              `{self._login_state_key}` int(11) DEFAULT '0' COMMENT '登录状态（0未登录 1已登录）',
              `{self._lock_state_key}` int(11) DEFAULT '0' COMMENT '账号是否被封（0 未封 1 被封）',
              PRIMARY KEY (`id`),
              UNIQUE KEY `username` (`username`) USING BTREE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self._mysqldb.execute(sql)

    def _load_user(self) -> Iterable[NormalUser]:
        """
        返回用户信息
        @return: yield username, password
        """

        keys = {
            'id': 'user_id',
            self._username_key: self._username_key,
            self._password_key: self._password_key
        }
        keys.update({key: key for key in self._table_keys or [] if key != 'id'})

        sql = make_query_sql(
            table=self._table_userbase,
            keys=keys,
            condition=f'{self._lock_state_key} = 0 and {self._login_state_key} = 0'
        )

        for data in self._mysqldb.find(sql, to_json=True):
            yield NormalUser(**data)

    def handle_login_failed_user(self, user: NormalUser):
        """
        处理登录失败的user
        @return:
        """

        pass

    def handel_exception(self, e: Exception):
        """
        处理异常
        @param e:
        @return:
        """
        log.exception(e)

    def login(self, user: NormalUser) -> NormalUser:
        """
        登录 生产cookie
        """
        raise NotImplementedError

    def add_user(self, user: NormalUser):
        log.debug("add {}".format(user))
        self._rdc.hset(self._tab_user_pool, user.user_id, user.to_dict())

        sql = "update {table_userbase} set {login_state_key} = 1 where id = {user_id}".format(
            table_userbase=self._table_userbase,
            login_state_key=self._login_state_key,
            username_key=self._username_key,
            user_id=user.user_id,
        )
        self._mysqldb.update(sql)

    def get_user(self, block=True) -> Optional[NormalUser]:
        """
        从用户池获取用户使用
        Args:
            block: 无用户时是否等待

        Returns:

        """
        while True:
            try:
                user_id = self._get_user_id()
                user_str = None
                if user_id:
                    user_str = self._rdc.hget(self._tab_user_pool, user_id)
                    # 如果没取到user，可能是其他爬虫将此用户删除了，需要重刷新本地缓存的用户id
                    if not user_str:
                        self._load_users_id()
                        continue

                if not user_id and block:
                    self._keep_alive = False
                    self.run()
                    continue

                return user_str and NormalUser(**eval(user_str))
            except Exception as e:
                log.exception(e)
                tools.delay_time(1)

    def del_user(self, user_id: int):
        """
        删除失效的user
        @return:
        """
        self._rdc.hdel(self._tab_user_pool, user_id)
        self._load_users_id()

        sql = "update {table_userbase} set {login_state_key} = 0 where id = {user_id}".format(
            table_userbase=self._table_userbase,
            login_state_key=self._login_state_key,
            username_key=self._username_key,
            user_id=user_id,
        )

        self._mysqldb.update(sql)

    def tag_user_locked(self, user_id: int, **kwargs):
        """
        标记用户被封堵
        @:param user_id: 用户id
        @:param kwargs: 其他需要更新的字段
        """
        kwargs[self._lock_state_key] = 1
        self._mysqldb.update_smart(
            table=self._table_userbase,
            data=kwargs,
            condition=f"id = {user_id}"
        )

    def run(self):
        while True:
            try:
                try:
                    with RedisLock(
                            key=self._tab_user_pool, lock_timeout=3600, wait_timeout=0, redis_cli=self._rdc
                    ) as _lock:
                        if _lock.locked:
                            for user in self._load_user():
                                retry_times = 0
                                while retry_times <= self._login_retry_times:
                                    try:
                                        login_user = self.login(user)
                                        if login_user:
                                            self.add_user(login_user)
                                        else:
                                            self.handle_login_failed_user(user)
                                        break
                                    except NotImplementedError:
                                        log.error(
                                            f"{self.__class__.__name__} must be implementation login method！"
                                        )
                                        os._exit(0)
                                    except Exception as e:
                                        self.handel_exception(e)
                                    log.debug(
                                        f"login failed, user: {user} retry_times: {retry_times}"
                                    )
                                    retry_times += 1
                                else:
                                    self.handle_login_failed_user(user)

                            now_user_count = self._rdc.hget_count(
                                self._tab_user_pool
                            )
                            log.info("当前在线user数为 {}".format(now_user_count))

                except Exception as e:
                    log.exception(e)

                if self._keep_alive:
                    tools.delay_time(10)
                else:
                    break

            except Exception as e:
                log.exception(e)
                tools.delay_time(1)
