'''
  Python test cases for Luncho server and client library.

  @author: HIRANO Satoshi
  @date: 2021-5-15
'''

from __future__ import annotations
import os
import time
from typing import cast, Any
import pytest
from fastapi.testclient import TestClient

import conf
import main
from src.types import CountryCode, LunchoData
from src import exchange_rate

@pytest.fixture(scope="function", autouse=True)
def setup_method() -> None:
    pass

def test_server_api() -> None:
    main.main(use_dummy_data=True)   # use dummy data from files
    client = TestClient(main.app)

    response = client.get("/v1/countries")
    assert response.status_code == 200
    data: dict[CountryCode, str] = response.json()
    assert data['JP'] == 'Japan'
    assert len(data) > 150

    response = client.get("/v1/luncho-data?country_code=JP")
    assert response.status_code == 200
    lunchoData: dict[str, Any] = response.json()
    Japan_test(lunchoData)

    response = client.get("/v1/all-luncho-data")
    assert response.status_code == 200
    data2: dict[CountryCode, dict[str, Any]] = response.json()
    Japan_test(data2['JP'])
    assert len(data2) > 150

    response = client.get("/v1/luncho-data?dummydata=JP")
    assert response.status_code == 422

def Japan_test(lunchoData: dict[str, Any]) -> None:
    assert lunchoData['country_code']   == 'JP'
    assert lunchoData['country_name']   == 'Japan'
    assert lunchoData['country_code']   == 'JP'
    assert lunchoData['continent_code'] == 'AS'
    assert lunchoData['currency_code']  == 'JPY'
    assert lunchoData['currency_name']  == 'Yen'
    assert lunchoData['exchange_rate']  == 105.40404976166664
    assert lunchoData['ppp']            == 87.827   # data/imf-dm-export-20221225.csv
    assert lunchoData['dollar_per_luncho'] == 0.07139819441152714
    assert lunchoData['expiration']     > time.time() + 60*60 - 2

def test_forex_api_down() -> None:
    ''' Test for Forex fetch error.

      Test:
        pytest test/test_server.py::test_server_api_error
    '''

    # no GCS
    conf.GCS_BUCKET = None

    # do without exchange_rate.Exchange_Rates and LAST_FIXER_EXCHANGE_FILE

    if os.path.exists(conf.EXCHANGE_RATE_FILE):
       os.remove(conf.EXCHANGE_RATE_FILE)
    exchange_rate.Exchange_Rates = {}

    conf.EXCHANGERATE_URLS = ['https://not_exist_not_exist.com']
    with pytest.raises(Exception):
        main.main(use_dummy_data=False)

    # do normally to make LAST_FIXER_EXCHANGE_FILE
    conf.EXCHANGERATE_URLS = conf.FREE_EXCHANGERATE_URLS
    main.main(use_dummy_data=False)
    assert os.path.exists(conf.EXCHANGE_RATE_FILE)

    # do with LAST_FIXER_EXCHANGE_FILE and without exchange_rate.Exchange_Rates
    exchange_rate.Exchange_Rates = {}
    conf.EXCHANGERATE_URLS = ['https://not_exsist_not_exist.com']
    main.main(use_dummy_data=False)

    # do with LAST_FIXER_EXCHANGE_FILE and with exchange_rate.Exchange_Rates
    conf.EXCHANGERATE_URLS = ['https://not_exsist_not_exist.com']
    main.main(use_dummy_data=False)

    # test exchange rate API fallback
    exchange_rate.Exchange_Rates = {}
    conf.EXCHANGERATE_URLS = ['https://not_exsist_not_exist.com'] + conf.FREE_EXCHANGERATE_URLS
    main.main(use_dummy_data=False)
