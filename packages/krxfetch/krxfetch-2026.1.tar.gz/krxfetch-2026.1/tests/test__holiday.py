import datetime

import pytest

from krxfetch._holiday import holiday_from_file
from krxfetch._holiday import holiday_from_krx


def test_holiday_from_file():
    info = holiday_from_file(2022)
    assert len(info) == 14
    assert info[0] == '2022-01-31'
    assert info[13] == '2022-12-30'

    info = holiday_from_file(2023)
    assert len(info) == 15
    assert info[0] == '2023-01-23'
    assert info[14] == '2023-12-29'

    info = holiday_from_file(2024)
    assert len(info) == 18
    assert info[0] == '2024-01-01'
    assert info[17] == '2024-12-31'

    info = holiday_from_file(2025)
    assert len(info) == 19
    assert info[0] == '2025-01-01'
    assert info[18] == '2025-12-31'

    info = holiday_from_file(2026)
    assert len(info) == 15
    assert info[0] == '2026-01-01'
    assert info[14] == '2026-12-31'

    info = holiday_from_file(2027)
    assert len(info) == 0


@pytest.mark.skipif(False, reason='requires http request')
def test_holiday_from_krx():
    info = holiday_from_krx(2026)
    assert len(info) == 15
    assert info[0] == '2026-01-01'
    assert info[14] == '2026-12-31'


@pytest.mark.skipif(False, reason='requires http request')
def test_maintenance():
    """If this test fails, update holiday_info() function."""

    tz = datetime.timezone(datetime.timedelta(hours=9))
    dt = datetime.datetime.now(tz=tz)

    assert holiday_from_file(dt.year) == holiday_from_krx(dt.year)
