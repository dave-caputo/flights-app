#!usr/bin/env python3


def format_to_data_table(func):
    def wrapper(*args, **kwargs):
        return {'data': func(*args, **kwargs)}
    return wrapper
