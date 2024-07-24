from datetime import datetime
from functools import wraps
import json.tool
from typing import Callable

import json.scanner
import requests


import urllib.parse
import json


def json_decode_error_handler(func: Callable):  # -> Callable:
    """
    Decorator to handle JSONDecodeError exceptions raised by a function.

    This decorator wraps a function and intercepts any JSONDecodeError exceptions that are raised.
    If such an exception occurs, it returns a string representation of the error instead of propagating the exception.
    Otherwise, it returns the result of the wrapped function.

    Args:
        func (Callable): The function to be wrapped.

    Returns:
        Callable: The wrapped function.

    Raises:
        None

    Examples:
        >>> @json_decode_error_handler
        >>> def get_json(url):
        >>>     response = requests.get(url)
        >>>     return response.json()
        >>>
        >>> get_json("https://invalid-json-url.com")
        "Expecting value: line 1 column 1 (char 0)"
    """

    @wraps(func)
    def wrapper(*args, **kwargs):  # -> Union[Any, str]:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.JSONDecodeError as e:
            return f"{e}"

    return wrapper


def time_ago(unix_time):
    now = datetime.now()
    timestamp = datetime.fromtimestamp(unix_time)
    delta = now - timestamp

    seconds = delta.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{int(minutes)} minutes ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{int(hours)} hours ago"
    elif seconds < 2592000:
        days = seconds // 86400
        return f"{int(days)} days ago"
    elif seconds < 31536000:
        months = seconds // 2592000
        return f"{int(months)} months ago"
    else:
        years = seconds // 31536000
        return f"{int(years)} years ago"


def round_num(num):
    abs_num = abs(num)
    if abs_num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif abs_num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif abs_num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


@json_decode_error_handler
def send_email(subject, text):
    url = "https://sandbox.api.mailtrap.io/api/send/3034355"

    headers = {
        "Authorization": "Bearer 60258dfa6c4d18a7f92b3108cd33d5aa",
        "Content-Type": "application/json",
    }

    data = {
        "from": {"email": "mailtrap@example.com", "name": "Mailtrap Test"},
        "to": [{"email": "nasiri.aliabdullah@gmail.com"}],
        "subject": subject,
        "text": text,
        "category": "Integration Test",
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()


def fragment2dct(fragment: str) -> dict:
    dct = {
        key: value
        for param in urllib.parse.unquote(fragment).split("&")
        for key, value in [param.split("=")]
    }

    for key, value in dct.items():
        try:
            dct[key] = json.loads(value)
        except json.JSONDecodeError:
            ...

    return dct
