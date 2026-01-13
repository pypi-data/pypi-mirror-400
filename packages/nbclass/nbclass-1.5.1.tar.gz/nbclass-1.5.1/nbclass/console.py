# -*- coding: utf-8 -*-
"""
@ Created on 2025-07-21 17:45
---------
@summary: 
---------
@author: XiaoBai
"""
import inspect

import unicodedata


class Console:
    COLORS = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'reset': 0,
    }
    STYLES = {
        'bold': 1,
        'underline': 4,
        'reverse': 7,
        'normal': 0,
    }

    @staticmethod
    def get_display_width(s):
        width = 0
        for ch in str(s):
            if unicodedata.east_asian_width(ch) in ('F', 'W'):
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def pad_display(s, width, align='left'):
        s = str(s)
        display_width = Console.get_display_width(s)
        pad_len = max(width - display_width, 0)
        if align == 'left':
            return s + ' ' * pad_len
        elif align == 'right':
            return ' ' * pad_len + s
        elif align == 'center':
            left = pad_len // 2
            right = pad_len - left
            return ' ' * left + s + ' ' * right
        else:
            return s

    @staticmethod
    def __color(*args, color='reset', style='normal', end='\n', sep=' ', file=None, flush=False, width=0, align='left'):
        frame = inspect.currentframe()
        try:
            # 向上追踪2层调用栈
            caller_frame = frame.f_back.f_back if frame.f_back else frame
            file_path = caller_frame.f_code.co_filename
            line_no = caller_frame.f_lineno
        finally:
            del frame  # 避免循环引用

        color_code = Console.COLORS.get(color, 0)
        style_code = Console.STYLES.get(style, 0)
        prefix = f'\033[{style_code};{color_code}m'
        suffix = '\033[0m'

        def format_arg(arg):
            s = str(arg)
            if width:
                s = Console.pad_display(s, width, align)
            return s

        formatted = sep.join(format_arg(a) for a in args)
        print(f"{file_path}:{line_no}: ", prefix, formatted, suffix, sep='', end=end, file=file, flush=flush)

    @staticmethod
    def info(*args, **kwargs):
        Console.__color(*args, color='reset', **kwargs)

    @staticmethod
    def red(*args, **kwargs):
        Console.__color(*args, color='red', **kwargs)

    @staticmethod
    def black(*args, **kwargs):
        Console.__color(*args, color='black', **kwargs)

    @staticmethod
    def green(*args, **kwargs):
        Console.__color(*args, color='green', **kwargs)

    @staticmethod
    def yellow(*args, **kwargs):
        Console.__color(*args, color='yellow', **kwargs)

    @staticmethod
    def blue(*args, **kwargs):
        Console.__color(*args, color='blue', **kwargs)

    @staticmethod
    def magenta(*args, **kwargs):
        Console.__color(*args, color='magenta', **kwargs)

    @staticmethod
    def cyan(*args, **kwargs):
        Console.__color(*args, color='cyan', **kwargs)

    @staticmethod
    def white(*args, **kwargs):
        Console.__color(*args, color='white', **kwargs)
