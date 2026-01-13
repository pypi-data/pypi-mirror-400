# (C) 2025 Fujitsu Limited
import json
import re


_snake_to_camel_pattern = re.compile(r'_([a-z])')


def snake_to_camel(snake_str: str) -> str:
    return _snake_to_camel_pattern.sub(lambda m: m.group(1).upper(), snake_str)


def snake_to_camel_keys(val: dict):
    if isinstance(val, dict):
        return {snake_to_camel(k): snake_to_camel_keys(v) for k, v in val.items()}
    else:
        return val


# From https://stackoverflow.com/a/1176023
_camel_to_snake_pattern = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')


def camel_to_snake(camel_str: str) -> str:
    return _camel_to_snake_pattern.sub('_', camel_str).lower()


def camel_to_snake_keys(val: dict):
    if isinstance(val, dict):
        return {camel_to_snake(k): camel_to_snake_keys(v) for k, v in val.items()}
    else:
        return val


def remove_none_values(dict_value: dict):
    return {k: v for k, v in dict_value.items() if v is not None}


def numpy_array_to_python_list(value):
    if hasattr(value, 'tolist'):
        return value.tolist()

    if isinstance(value, list):  # for handling the case of list[numpy.ndarray]
        return [numpy_array_to_python_list(one_val) for one_val in value]

    return value


def find_duplicates(list_value: list) -> set:
    seen = set()
    duplicates = set()
    for item in list_value:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates


def serialize_numpy_to_json(obj):
    if obj.__class__.__module__ == 'numpy':
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()

        # raise an error for np.complexfloating

    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def json_dumps(obj, *args, **kwargs):
    kwargs_copy = kwargs.copy()
    if 'default' not in kwargs:
        kwargs_copy['default'] = serialize_numpy_to_json

    return json.dumps(obj, *args, **kwargs_copy)
