# Copyright (C) 2025 Tao Yuan
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

import time
from typing import Callable

from yuantao_fmk import Config, logger


def print_result(func):
    def wrapper(*args, **kwargs):
        return_val = func(*args, **kwargs)
        print(return_val)
        return return_val

    return wrapper


def print_args(func):
    def wrapper(*args, **kwargs):
        print("args:", args)
        print("kwargs:", kwargs)
        return func(*args, **kwargs)

    return wrapper


def print_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        return_val = func(*args, **kwargs)
        print("执行函数%s,用时%d" % (func, time.time() - start_time))
        return return_val if return_val else None

    return wrapper


def dryrun(func: Callable) -> Callable:
    if Config.DRYRUN:
        return lambda *args, **kwargs: logger.debug(
            f"Dryrun: {func.__name__}, args={args}, kwargs={kwargs}"
        )
    else:
        return func
