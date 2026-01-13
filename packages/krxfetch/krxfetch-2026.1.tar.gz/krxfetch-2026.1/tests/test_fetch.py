import pytest

from krxfetch.fetch import get_json_data
from krxfetch.fetch import download_csv


@pytest.fixture
def payload():
    """[11001] 통계 > 기본 통계 > 지수 > 주가지수 > 전체지수 시세"""

    return {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT00101',
        'locale': 'ko_KR',
        'idxIndMidclssCd': '01',
        'trdDd': '20250812',
        'share': '2',
        'money': '3',
        'csvxls_isNo': 'false'
    }


@pytest.mark.skipif(False, reason='requires http request')
def test_get_json_data(payload):
    data = get_json_data(payload)

    assert data[0]['IDX_NM'] == '코리아 밸류업 지수'
    assert data[0]['CLSPRC_IDX'] == '1,265.58'
    assert data[0]['FLUC_TP_CD'] == '2'
    assert data[0]['CMPPREVDD_IDX'] == '-0.87'
    assert data[0]['FLUC_RT'] == '-0.07'
    assert data[0]['OPNPRC_IDX'] == '1,270.51'
    assert data[0]['HGPRC_IDX'] == '1,286.20'
    assert data[0]['LWPRC_IDX'] == '1,264.83'
    assert data[0]['ACC_TRDVOL'] == '47,416,839'
    assert data[0]['ACC_TRDVAL'] == '4,510,708,123,755'
    assert data[0]['MKTCAP'] == '1,343,651,105,317,310'

    assert len(data[0]) == 11


@pytest.mark.skipif(False, reason='requires http request')
def test_download_csv(payload):
    bld = payload.pop('bld')
    payload['name'] = 'fileDown'
    payload['url'] = bld

    csv = download_csv(payload)

    lines = csv.splitlines()

    assert lines[0] == '지수명,종가,대비,등락률,시가,고가,저가,거래량,거래대금,상장시가총액'
    assert lines[1] == '"코리아 밸류업 지수","1265.58","-0.87","-0.07","1270.51","1286.20","1264.83","47417.0","4510708.0","1.343651105E9"'
