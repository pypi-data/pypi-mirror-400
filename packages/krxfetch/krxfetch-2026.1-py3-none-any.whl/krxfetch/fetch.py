import requests

from . import _chrome


def get_json_data(payload: dict, referer: str | None = None) -> list[dict]:
    if referer is None:
        referer = 'https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd?menuId=MDC0201'

    headers = {
        'user-agent': _chrome.user_agent(),
        'referer': referer
    }

    url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

    r = requests.post(url=url, data=payload, headers=headers)
    json = r.json()

    keys = list(json)
    k = keys[1] if keys[0] == 'CURRENT_DATETIME' else keys[0]

    if k != 'output' and k != 'OutBlock_1' and k != 'block1':
        raise NotImplementedError(k)

    return json[k]


def download_csv(payload: dict, referer: str | None = None) -> str:
    if referer is None:
        referer = 'https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd?menuId=MDC0201'

    headers = {
        'user-agent': _chrome.user_agent(),
        'referer': referer
    }

    # 1. Generate OTP
    otp_url = 'https://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'

    r = requests.post(url=otp_url, data=payload, headers=headers)
    otp = {
        'code': r.text
    }

    # 2. Download CSV
    url = 'https://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'

    r = requests.post(url=url, data=otp, headers=headers)
    csv = r.content.decode(encoding='euc_kr')

    return csv
