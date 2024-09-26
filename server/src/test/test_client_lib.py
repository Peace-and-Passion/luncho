'''

  pytest test/test_client_lib.py
  pytest test/test_client_lib.py::test_countries_luncho


  This test does not run in Emacs. Why?

  @author HIRANO Satoshi
  @date  2021/5/18
'''
import pytest

import luncho_python
from luncho_python.api import luncho_api, luncho
from luncho_python.model.luncho_data import LunchoData

CountryCode = str

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = luncho_python.Configuration(
    host = "http://localhost:8000"
)


class Test:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.api_client: luncho_python.ApiClient = luncho_python.ApiClient(configuration)
        self.luncho: luncho.Luncho                # local API  (Use this in your app!)
        self.lunchoRemote: luncho_api.LunchoApi   # remote API

    def test_get_currency_from_luncho(self) -> None:
        self.luncho = luncho.Luncho(self.api_client)
        assert self.luncho.get_currency_from_luncho(100.0, 'JP') >= 500
        assert self.luncho.get_currency_from_luncho(100.0, 'JP') >= 500  # again to test cache
        assert self.luncho.get_currency_from_luncho(100.0, 'JP', factor=0.2) < 200  # again to test cache

    def test_local_get_luncho_from_currency(self) -> None:
        pass

    def test_get_currency_from_US_dollar(self) -> None:
        self.luncho = luncho.Luncho(self.api_client)
        assert self.luncho.get_currency_from_US_dollar(50.0, 'JP') == 4391.35
        assert self.luncho.get_currency_from_US_dollar(50.0, 'JP') == 4391.35  # again to test cache
        assert self.luncho.get_currency_from_US_dollar(50.0, 'JP', factor=0.2) == 918.2700000000001

    def test_get_US_dollar_from_luncho(self) -> None:
        self.luncho = luncho.Luncho(self.api_client)
        assert self.luncho.get_US_dollar_from_luncho(100.0, 'JP') > 4.0
        assert self.luncho.get_US_dollar_from_luncho(100.0, 'JP') > 4.0  # again to test cache
        assert self.luncho.get_US_dollar_from_luncho(100.0, 'JP', factor=0.2) > 6  # again to test cache

    def test_get_countries(self) -> None:
        self.luncho = luncho.Luncho(self.api_client)
        assert len(self.luncho.get_countries()) > 150
        assert len(self.luncho.get_countries()) > 150   # again to test cache

    def test_countries_luncho_remote(self) -> None:
        self.lunchoRemote = luncho_api.LunchoApi(self.api_client)
        assert len(self.lunchoRemote.countries()) > 150

    def test_get_luncho_data(self) -> None:
        self.luncho = luncho.Luncho(self.api_client)

        Japan_test(self.luncho.get_luncho_data('JP'))
        Japan_test(self.luncho.get_luncho_data('JP'))  # again should use cache

        with pytest.raises(luncho_python.ApiException):
            self.luncho.get_luncho_data('NOT EXISTS')

    def test_luncho_data_luncho_remote(self) -> None:
        self.lunchoRemote = luncho_api.LunchoApi(self.api_client)
        Japan_test(self.lunchoRemote.luncho_data('JP'))

    def test_get_all_luncho_data(self) -> None:
        self.luncho = luncho.Luncho(self.api_client)
        lunchoDatas: dict[CountryCode, LunchoData] = self.luncho.get_all_luncho_data()
        Japan_test(lunchoDatas['JP'])

        lunchoDatas = self.luncho.get_all_luncho_data()   # again to test cache
        Japan_test(lunchoDatas['JP'])

    def test_all_luncho_data_luncho_remote(self) -> None:
        self.lunchoRemote = luncho_api.LunchoApi(self.api_client)
        lunchoDatas: dict[CountryCode, LunchoData] = self.lunchoRemote.all_luncho_data()
        Japan_test(lunchoDatas['JP'])


def Japan_test(lunchoData: LunchoData) -> None:
    assert lunchoData['country_code']   == 'JP'
    assert lunchoData['country_name']   == 'Japan'
    assert lunchoData['country_code']   == 'JP'
    assert lunchoData['continent_code'] == 'AS'
    assert lunchoData['currency_code']  == 'JPY'
    assert lunchoData['currency_name']  == 'Yen'
    assert lunchoData['exchange_rate']  > 80
    assert lunchoData['ppp']            > 80
    assert lunchoData['dollar_per_luncho'] > 0.04
    #assert lunchoData['expiration']     > time.time() + 60*60 - 2
