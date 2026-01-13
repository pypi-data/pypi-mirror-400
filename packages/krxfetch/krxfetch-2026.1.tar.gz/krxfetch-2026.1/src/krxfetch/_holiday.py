import os.path
import time

import requests

from . import _chrome


def holiday_from_file(year: int) -> list:
    """Return holiday info from a local file."""

    file = os.path.join(os.path.dirname(__file__), 'data', f'holiday_{year}.dat')

    try:
        with open(file, encoding='utf-8') as f:
            holiday = f.read().splitlines()
    except OSError:
        holiday = list()

    return holiday


def holiday_from_krx(year: int) -> list:
    """Fetch holiday info from KRX."""

    headers = {
        'user-agent': _chrome.user_agent()
    }

    # 1. Generate OTP
    otp_url = 'http://open.krx.co.kr/contents/COM/GenerateOTP.jspx'
    payload = {
        'bld': 'MKD/01/0110/01100305/mkd01100305_01',
        'name': 'form',
        '_': int(time.time() * 1000)  # timestamp
    }

    r = requests.get(url=otp_url, params=payload, headers=headers)

    # 2. holiday
    url = 'http://open.krx.co.kr/contents/OPN/99/OPN99000001.jspx'
    payload = {
        'search_bas_yy': str(year),
        'gridTp': 'KRX',
        'pagePath': '/contents/MKD/01/0110/01100305/MKD01100305.jsp',
        'code': r.text
    }

    r = requests.post(url=url, data=payload, headers=headers)
    json = r.json()

    holiday = [item['calnd_dd'] for item in json['block1']]

    return holiday
