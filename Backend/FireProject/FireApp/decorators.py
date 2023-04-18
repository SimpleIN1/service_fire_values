import functools
import time

import jwt
from django.db import connection
from rest_framework import exceptions, status


def query_debugger(func):

    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        # reset_queries()

        start_queries = len(connection.queries)

        print(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        for item in connection.queries:
            print(item)

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.4f}s")
        return result

    return inner_func


def debug_time_func(func):

    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'Time of work func {func.__name__} : {(end - start):.4f}s')
        return result
    return inner_func


def exception_jwt(func):

    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        try:
            result = func(*args, **kwargs)
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed(
                {'error_token': '14'},
                # code=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                {'error_token': '15'},
                # code=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed(
                {'error_token': '16'},
                # code=status.HTTP_401_UNAUTHORIZED
            )

        return result

    return inner_func