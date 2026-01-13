# -*- coding: utf-8 -*-
"""
@ Created on 2025-02-05 14:08
---------
@summary: 
---------
@author: XiaoBai
"""
import functools
import threading
import time
from typing import Type, TypeVar, Callable, Dict, Any, Optional, Union

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec
from nbclass.log import logger

T = TypeVar('T')
P = ParamSpec('P')


def keep_time(func: Callable[P, T]) -> Callable[P, T]:
    # 计算函数运行时间
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        s = time.time()
        data = func(*args, **kwargs)
        runtime = (time.time() - s) * 1000
        logger.warning(f"{func.__name__} 耗时: {runtime} ms")
        return data

    return wrapper


def lock_decorator(lock=threading.Lock()):
    """ 线程锁保护 防止多线程资源竞争。 """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def memoize(func):
    """ 缓存函数结果避免重复计算，显著加速递归或高开销函数 """
    cache = {}

    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper


def retry(retry_times: int = 3, interval: Union[float, int] = 0, tag: Optional[Any] = False) -> Callable:
    """
    普通函数的重试装饰器
    Args:
        retry_times: 重试次数
        interval: 每次重试之间的间隔
        tag: 自定义的异常返回值
    Returns:

    """

    def _retry(func: Callable) -> Callable:
        @functools.wraps(func)  # 将函数的原来属性付给新函数
        def wrapper(*args, **kwargs):
            for i in range(retry_times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        "函数 {}:{} 执行失败 重试 {} 次. error {}".format(func.__name__, e.__traceback__.tb_next.tb_lineno, i, e)
                    )
                    time.sleep(interval)
                    if i >= retry_times:
                        return tag

        return wrapper

    return _retry


def singleton(cls: Type[T]) -> Callable[..., T]:
    instances: Dict[tuple, Any] = {}

    @functools.wraps(cls)
    def wrapper(*args, **kwargs) -> T:
        key = (args, frozenset(kwargs.items()))
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return wrapper


def threaded(func):
    """ 函数线程化 将阻塞函数转为后台线程。 """

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


timer = keep_time
