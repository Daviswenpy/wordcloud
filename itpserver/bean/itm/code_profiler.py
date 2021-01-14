# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-08-02 17:52:26
File Name: code_profiler.py @v1.0
"""
import time
from functools import wraps

import cProfile
from line_profiler import LineProfiler


__all__ = ['func_time', 'func_cprofile', 'func_line_time']


"""
# docs
# from .code_profiler import func_line_time
# @func_line_time
# tar_func():
#     pass
"""


def func_time(f):
    """
    Only profile time.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f.__name__, 'took', end - start, 'seconds')
        return result

    return wrapper


def func_cprofile(f):
    """
    Func profile.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = f(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort='time')

    return wrapper


try:
    def func_line_time(follow=[]):
        """
        Profile for every code line.
        """
        def decorate(func):
            @wraps(func)
            def profiled_func(*args, **kwargs):
                try:
                    profiler = LineProfiler()
                    profiler.add_function(func)

                    for f in follow:
                        profiler.add_function(f)

                    profiler.enable_by_count()
                    return func(*args, **kwargs)
                finally:
                    profiler.print_stats()
            return profiled_func
        return decorate

except ImportError:
    def func_line_time(follow=[]):
        "Helpful if you accidentally leave in production!"
        def decorate(func):
            @wraps(func)
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return nothing
        return decorate
