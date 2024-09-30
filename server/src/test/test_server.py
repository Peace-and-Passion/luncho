'''
  Python test cases for Luncho server and client library.

  @author: HIRANO Satoshi
  @date: 2021-5-15
'''

import os
import sys
import time

# add path to luncho_pypyenv
current_dir = os.path.dirname(os.path.abspath(__file__))
pypyenv_path = os.path.join(current_dir, '../../luncho_pypyenv/bin')
if pypyenv_path not in sys.path:
    sys.path.insert(0, pypyenv_path)

# luncho_pypyenv/bin/activate
activate_this = os.path.join(pypyenv_path, 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

#
from typing import cast, Any
import pytest
from fastapi.testclient import TestClient

import conf
conf.GCS_BUCKET = None         # no GCS

import main
from src.types import CountryCode, LunchoData
from src import exchange_rate, ppp_data

@pytest.fixture(scope="function", autouse=True)
def setup_method() -> None:
    pass

def test_server_api() -> None:
    ''' test API functions using dummy files.

      Test:
        pytest src/test/test_server.py::test_server_api
    '''

    main.main(use_test_data=True)   # use dummy data from files
    client = TestClient(main.app)

    response = client.get("/v1/countries")
    assert response.status_code == 200
    data: dict[CountryCode, str] = response.json()
    assert data['JP'] == 'Japan'
    assert len(data) > 150

    response = client.get("/v1/luncho-data?country_code=JP")
    assert response.status_code == 200
    lunchoData: dict[str, Any] = response.json()
    _Japan_test(lunchoData)

    response = client.get("/v1/all-luncho-data")
    assert response.status_code == 200
    data2: dict[CountryCode, LunchoData] = response.json()
    _Japan_test(data2['JP'])
    assert len(data2) > 150

    # test ppp exist
    ld: LunchoData
    cc: str
    for cc, ld in data2.items():
        assert ld.get('ppp') != None

    response = client.get("/v1/luncho-data?dummydata=JP")
    assert response.status_code == 422

def _Japan_test(lunchoData: dict[str, Any]) -> None:
    ''' test values using dummy files. '''

    assert lunchoData['country_code']   == 'JP'
    assert lunchoData['country_name']   == 'Japan'
    assert lunchoData['country_code']   == 'JP'
    assert lunchoData['continent_code'] == 'AS'
    assert lunchoData['currency_code']  == 'JPY'
    assert lunchoData['currency_name']  == 'Yen'
    assert lunchoData['exchange_rate']  == 144.82208333
    assert lunchoData['ppp']            == 90.821   # 2024 JPN in data/dummy-ppp-data-2024-09-26.json
    assert lunchoData['dollar_per_luncho'] == 0.14954671741828893
    assert lunchoData['expiration']     > time.time() + 60*60 - 2

def test_load_data() -> None:
    ''' Test load_data() with exchange rates.

    1) test fetch with API without backup file.
    2) test load from backup file.
    3) test fetch with API failure, then load from the backup file.
    4) test fetch with API failure and no backup file. Use existing Exchange_Rates.
    5) test fetch with API failure and no backup file and no existing Exchange_Rates. Abort.

      Test:
        pytest src/test/test_server.py::test_load_data
    '''

    # no GCS
    conf.GCS_BUCKET = None

    # do without exchange_rate.Exchange_Rates and LAST_FIXER_EXCHANGE_FILE

    if os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE)):
       os.remove(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    exchange_rate.Exchange_Rates = {}

    # 1) test fetch with API without backup file.

    exchange_rate.load_exchange_rates(use_test_data=False)
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    assert exchange_rate.data_source == 'API'

    # 2) test load from backup file.

    exchange_rate.load_exchange_rates(use_test_data=False)
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    assert exchange_rate.data_source == 'backup'

    # 3) test fetch with API failure, then load from the backup file.

    url = conf.EXCHANGE_RATE_URL
    conf.EXCHANGE_RATE_URL = 'https://not_exist_not_exist.com'
    exchange_rate.load_exchange_rates(use_test_data=False)
    conf.EXCHANGE_RATE_URL = url
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    assert exchange_rate.data_source == 'backup'

    # 4) test fetch with API failure and no backup file. Use existing Exchange_Rates.

    url = conf.EXCHANGE_RATE_URL
    conf.EXCHANGE_RATE_URL = 'https://not_exist_not_exist.com'
    os.remove(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    exchange_rate.load_exchange_rates(use_test_data=False)
    conf.EXCHANGE_RATE_URL = url
    assert exchange_rate.data_source == 'fail'

    # 5) test fetch with API failure and no backup file and no existing Exchange_Rates. Abort.

    url = conf.EXCHANGE_RATE_URL
    conf.EXCHANGE_RATE_URL = 'https://not_exist_not_exist.com'
    exchange_rate.Exchange_Rates = {}
    with pytest.raises(AssertionError):
        exchange_rate.load_exchange_rates(use_test_data=False)
    conf.EXCHANGE_RATE_URL = url


    # # do with EXCHANGE_RATE_FILE and without exchange_rate.Exchange_Rates
    # exchange_rate.Exchange_Rates = {}
    # conf.EXCHANGE_RATE_URL = 'https://not_exsist_not_exist.com'
    # exchange_rate.load_exchange_rates(use_test_data=False)

    # # do with EXCHANGE_RATE_FILE and with exchange_rate.Exchange_Rates
    # conf.EXCHANGE_RATE_URL = 'https://not_exsist_not_exist.com'
    # exchange_rate.load_exchange_rates(use_test_data=False)

def test_update_exchange_rate() -> None:
    ''' Test update_exchange_rate() with exchange rates.

    1) test fetch with API without backup file.
    2) test fetch with API with backup file.
    3) test fetch with API failure, then load from the backup file.
    4) test fetch with API failure and no backup file. Use existing Exchange_Rates.
    5) test fetch with API failure and no backup file and no existing Exchange_Rates. Abort.

      Test:
        pytest src/test/test_server.py::test_load_data
    '''

    # no GCS
    conf.GCS_BUCKET = None

    # do without exchange_rate.Exchange_Rates and LAST_FIXER_EXCHANGE_FILE

    if os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE)):
       os.remove(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    exchange_rate.Exchange_Rates = {}

    main.main(use_test_data=True)   # use dummy data from files
    client = TestClient(main.app)

    # 1) test fetch with API without backup file.

    response = client.get("/v1/update_exchange_rate")
    assert response.status_code == 200
    assert exchange_rate.data_source == 'API'
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))

    # 2) test fetch with API with backup file.

    response = client.get("/v1/update_exchange_rate")
    assert response.status_code == 200
    assert exchange_rate.data_source == 'API'
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))

    # 3) test fetch with API failure, then load from the backup file.

    url = conf.EXCHANGE_RATE_URL
    conf.EXCHANGE_RATE_URL = 'https://not_exist_not_exist.com'
    response = client.get("/v1/update_exchange_rate")
    assert response.status_code == 200
    conf.EXCHANGE_RATE_URL = url
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    assert exchange_rate.data_source == 'backup'

    # 4) test fetch with API failure and no backup file. Use existing Exchange_Rates.

    url = conf.EXCHANGE_RATE_URL
    conf.EXCHANGE_RATE_URL = 'https://not_exist_not_exist.com'
    os.remove(os.path.join(conf.Data_Dir, conf.EXCHANGE_RATE_FILE))
    response = client.get("/v1/update_exchange_rate")
    assert response.status_code == 200
    conf.EXCHANGE_RATE_URL = url
    assert exchange_rate.data_source == 'fail'

    # 5) test fetch with API failure and no backup file and no existing Exchange_Rates. Abort.

    url = conf.EXCHANGE_RATE_URL
    conf.EXCHANGE_RATE_URL = 'https://not_exist_not_exist.com'
    exchange_rate.Exchange_Rates = {}
    with pytest.raises(AssertionError):
        response = client.get("/v1/update_exchange_rate")
    # assert response.status_code == 500
    # conf.EXCHANGE_RATE_URL = url
    # assert exchange_rate.data_source == 'fail'

def test_update_ppp_data() -> None:
    ''' Test update_ppp_data() with exchange rates.

    1) test fetch with API without backup file.
    2) test fetch with API with backup file.
    3) test fetch with API failure, then load from the backup file.
    4) test fetch with API failure and no backup file. Use existing Ppp_Datas.
    5) test fetch with API failure and no backup file and no existing Ppp_Datas. Abort.

      Test:
        pytest src/test/test_server.py::test_load_data
    '''

    # no GCS
    conf.GCS_BUCKET = None

    # do without ppp_data.Ppp_Datas and LAST_FIXER_EXCHANGE_FILE

    if os.path.exists(os.path.join(conf.Data_Dir, conf.PPP_DATA_FILE)):
       os.remove(os.path.join(conf.Data_Dir, conf.PPP_DATA_FILE))
    ppp_data.Countries = {}

    main.main(use_test_data=True)   # use dummy data from files
    client = TestClient(main.app)

    # 1) test fetch with API without backup file.

    response = client.get("/v1/update_ppp_data")
    assert response.status_code == 200
    assert ppp_data.data_source == 'API'
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.PPP_DATA_FILE))

    # 2) test fetch with API with backup file.

    response = client.get("/v1/update_ppp_data")
    assert response.status_code == 200
    assert ppp_data.data_source == 'API'
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.PPP_DATA_FILE))

    # 3) test fetch with API failure, then load from the backup file.

    url = conf.PPP_DATA_URL
    conf.PPP_DATA_URL = 'https://not_exist_not_exist.com'
    response = client.get("/v1/update_ppp_data")
    assert response.status_code == 200
    conf.PPP_DATA_URL = url
    assert os.path.exists(os.path.join(conf.Data_Dir, conf.PPP_DATA_FILE))
    assert ppp_data.data_source == 'backup'

    # 4) test fetch with API failure and no backup file. Use existing Countries.

    url = conf.PPP_DATA_URL
    conf.PPP_DATA_URL = 'https://not_exist_not_exist.com'
    os.remove(os.path.join(conf.Data_Dir, conf.PPP_DATA_FILE))
    response = client.get("/v1/update_ppp_data")
    assert response.status_code == 200
    conf.PPP_DATA_URL = url
    assert ppp_data.data_source == 'fail'

    # 5) test fetch with API failure and no backup file and no existing Countries. Abort.

    url = conf.PPP_DATA_URL
    conf.PPP_DATA_URL = 'https://not_exist_not_exist.com'
    ppp_data.Countries = {}
    with pytest.raises(AssertionError):
        response = client.get("/v1/update_ppp_data")
    # assert response.status_code == 500
    # conf.ppp_data_URL = url
    # assert exchange_rate.data_source == 'fail'
