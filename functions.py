import json
import json.scanner
import json.tool
import random
import urllib.parse
from datetime import datetime
from typing import List, Union

import requests


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

    if response.status_code == 200:
        return response.json()
    return {}


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


def check_socks_proxy(proxy) -> Union[bool, None]:
    url = (
        "http://httpbin.org/ip"  # This endpoint returns the IP address of the requester
    )
    proxies = {
        "socks4": proxy,
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException:
        ...


def get_random_socks_proxy() -> Union[dict, None]:
    with open("proxies.txt", "rt", encoding="UTF-8") as file:
        lines: List[str] = [line.strip() for line in file.readlines()]

        count = 0
        while count < 10:
            proxy = random.choice(lines)
            if check_socks_proxy(proxy):
                print(f"Proxy {proxy} is working.")

                return {"socks4": proxy}
            else:
                print(f"Proxy {proxy} is not working.")

            count += 1

        return None
