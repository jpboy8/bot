import functools
import time


def repeat_if_failed(count: int, timeout: int = 1, handled_exceptions=None):
    handled_exceptions = handled_exceptions or (Exception,)

    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            data = {}
            while attempt < count:
                attempt += 1
                try:
                    data = func(*args, **kwargs)
                except handled_exceptions:
                    print(attempt)
                    print(handled_exceptions)
                    time.sleep(timeout)
                else:
                    break
            return data

        return wrapper

    return inner_function
