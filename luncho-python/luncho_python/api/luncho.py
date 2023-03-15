'''
   Fast Luncho API client with caching. Use this and don't this LunchoApi.py.

  @author: HIRANO Satoshi
  @date: 2021-5-18
'''
import time
#import pdb; pdb.set_trace()
from typing import List, Dict, Tuple, Callable, Union, Any, Set, ClassVar, Type, Optional, cast

from luncho_python.api.luncho_api import LunchoApi
from luncho_python.api_client import ApiClient, Endpoint as _Endpoint
from luncho_python.model.luncho_data import LunchoData

CountryCode = str

class Luncho():
    ''' Fast Luncho API client by caching.
        This class converts values between Luncho and a specified currency using cached
        LunchoData. If the cache is not available, it delegates to LunchoApi which
        is a auto-generated class.

        In the cases of error, methods raise luncho_python.ApiException.
        Note that no async_req argument is supported.
    '''

    def __init__(self, api_client=None) -> None:
        self.lunchoApi = LunchoApi(api_client)             # for delegation

        self.lunchoDataCache: Dict[CountryCode, LunchoData] = {}  # Cache {CountryCode: LunchoData}
        self.allLunchoDatasExpiration: float = 0.0
        self.countryCache: Dict[CountryCode, str] = {}       # { CountryCode: name }
        self.countryCodeCache: str


    def get_currency_from_luncho(self, lunchoValue: float, countryCode: str, factor: float = 1.0, **kwargs) -> float:
        '''
          Returns a local currency value from the given Luncho value for the specified country.

          @param lunchoValue A Luncho value to be converted.
          @param countryCode A 2-letter country code. The result is in the primary currency of the country.
          @param factor      A number how much the price level considered (reflected).
                             0 for no consideration and 1.0 for full consideration.
          @return A value in local currency for the lunchoValue.
        '''

        lunchoData: LunchoData = self.get_luncho_data(countryCode, **kwargs)

        US_value = lunchoData.dollar_per_luncho * lunchoValue
        local_currency_value = US_value * lunchoData.ppp
        local_currency_value_with_factor = US_value - (US_value - local_currency_value) * factor
        return local_currency_value_with_factor

    def get_luncho_from_currency(self, lunchoValue: float, countryCode: str, **kwargs) -> float:
        '''
          Returns a Luncho value from a local currency value for the specified country.

          @param localValue A value in local currency to be converted.
          @param countryCode A 2-letter country code of the country for the localValue.
          @return A value in Luncho for the localValue.
        '''

        assert False, 'XXX Implement me'
        return 0.0

    def get_US_dollar_from_luncho(self, lunchoValue: float, countryCode: str, factor: float = 1.0, **kwargs) -> float:
        '''
          Returns a US Dollar value from the given Luncho value for the specified country.

          @param lunchoValue A Luncho value to be converted.
          @param countryCode A 2-letter country code.
          @param factor      A number how much the price level considered (reflected).
                             0 for no consideration and 1.0 for full consideration.
          @return A value in US dollar for the lunchoValue.
        '''

        lunchoData: LunchoData = self.get_luncho_data(countryCode, **kwargs)
        if lunchoData.exchange_rate > 0:
            US_value = lunchoData.dollar_per_luncho * lunchoValue;
            local_currency_value = US_value * lunchoData.ppp;
            dollar_value = local_currency_value / lunchoData.exchange_rate;
            dollar_value_with_factor = US_value - (US_value - dollar_value) * factor;
            return dollar_value_with_factor;
        return 0.0

    def get_luncho_from_US_dollar(self, lunchoValue: float, countryCode: str, **kwargs) -> float:
        '''
          Returns a Luncho value from a US Dollar value for the specified country.

          @param dollarValue A value in US dollar to be converted.
          @param countryCode A 2-letter country code of the country.
          @return Promise for a value in Luncho for the dollarValue.
        '''

        assert False, 'XXX Implement me'
        return 0.0

    def get_countries(self, **kwargs) -> Dict[CountryCode, str]:
        '''
          Returns a dict of supported country codes and country names.
        '''

        if self.countryCache:
            return self.countryCache

        self.countryCache = self.lunchoApi.countries(**kwargs)
        return self.countryCache

    def get_luncho_data(self, country_code: CountryCode, **kwargs) -> LunchoData:
        '''
           Returns a LunchoData of the specified country code. You don't need to use this method
           usually. Use localCurrencyFromLuncho() and get_US_dollar_from_luncho().

           @param param A LunchoDataRequest object.
           @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
           @return A LunchoData for the country_code.
        '''

        lunchoData: Optional[LunchoData] = self.lunchoDataCache.get(country_code)
        if lunchoData and lunchoData.expiration > time.time():
            return lunchoData

        lunchoData = cast(LunchoData, self.lunchoApi.luncho_data(country_code, **kwargs))
        self.lunchoDataCache[country_code] = lunchoData
        return lunchoData

    def get_all_luncho_data(self, **kwargs) -> Dict[CountryCode, LunchoData]:
        '''
          Returns a dict of LunchoDatas of all countries. You don't need to use this method
           usually. Use localCurrencyFromLuncho() and get_US_dollar_from_luncho().
        '''
        if self.allLunchoDatasExpiration > time.time():
            return self.lunchoDataCache

        self.lunchoDataCache = self.lunchoApi.all_luncho_data(**kwargs)
        assert self.lunchoDataCache
        assert self.lunchoDataCache['JP']
        self.allLunchoDatasExpiration = self.lunchoDataCache['JP'].expiration
        return self.lunchoDataCache


    def get_country_code(self, **kwargs) -> str:
        '''
         Returns an estimated country code with IP address. Available only if the server supports.
        '''

        if self.countryCodeCache:
            return self.countryCodeCache

        self.countryCodeCache = self.lunchoApi.country_code(**kwargs)
        return self.countryCodeCache

    def __getattr__(self, method_name):
        ''' Delegates all other methods to self.lunchoApi. '''

        def method(*args, **kwargs):
            return getattr(self.lunchoApi, method_name)(*args, **kwargs)
        return method
