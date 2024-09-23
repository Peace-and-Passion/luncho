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
CurrencyCode = str

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
        self.exchangeRatesCache: Dict[CurrencyCode, float]  = {} # exchange rates cache


    def get_currency_from_US_dollar(self, usdValue: float, countryCode: str, factor: float = 1.0, **kwargs) -> float:
        '''
          Returns the local currency value of the country from the US dollar value in US, taking the
          price level of the country into account by factor 0 to 1.0.

          @param lunchoValue A Luncho value to be converted.
          @param countryCode A 2-letter country code. The result is in the primary currency of the country.
          @param factor      A number how much the price level considered (reflected).
                             0 for no consideration and 1.0 for full consideration.
          @return A value in local currency for the lunchoValue.
        '''

        lunchoData: LunchoData = self.get_luncho_data(countryCode, **kwargs)

        local_currency_value = usdValue * lunchoData.ppp
        local_currency_value_with_factor = usdValue - (usdValue - local_currency_value) * factor
        return local_currency_value_with_factor

    def get_currency_from_luncho(self, lunchoValue: float, countryCode: str, factor: float = 1.0, **kwargs) -> float:
        '''
        Returns the local currency value of the country from the Luncho value, taking the
        price level of the country into account by factor 0 to 1.0.

          @param lunchoValue A Luncho value to be converted.
          @param countryCode A 2-letter country code. The result is in the primary currency of the country.
          @param factor      A number how much the price level be reflected.
                             0 for no consideration and 1.0 for full consideration.
          @return A value in local currency for the lunchoValue.

        '''

        lunchoData: LunchoData = self.get_luncho_data(countryCode, **kwargs)

        US_value = lunchoData.dollar_per_luncho * lunchoValue;
        local_currency_value = US_value * lunchoData.ppp;
        dollar_value = local_currency_value / lunchoData.exchange_rate;
        dollar_value_with_factor = US_value - (US_value - dollar_value) * factor;

        local_currency_value_with_factor = dollar_value_with_factor * lunchoData.exchange_rate;
        return local_currency_value_with_factor

        # US_value = lunchoData.dollar_per_luncho * lunchoValue
        # local_currency_value = US_value * lunchoData.ppp
        # local_currency_value_with_factor = US_value - (US_value - local_currency_value) * factor

    def get_luncho_from_currency(self, currencyValue: float, countryCode: str, **kwargs) -> float:
        '''
          Returns the Luncho value of the country from the local currency value.

          @param localValue A value in local currency to be converted.
          @param countryCode A 2-letter country code of the country for the localValue.
          @return A value in Luncho for the localValue.
        '''

        lunchoData: LunchoData = self.get_luncho_data(countryCode, **kwargs)

        luncho_value = currencyValue / lunchoData.ppp
        return luncho_value

    def get_US_dollar_from_luncho(self, lunchoValue: float, countryCode: str, factor: float = 1.0, **kwargs) -> float:
        '''
       Returns the US Dollar value of a country from a Luncho value.

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
        Load and get a dict of LunchoData of all supported countries.  Data size is about 40KB.
        If you use data of all countries, call this before in order to load all LunchoDatas at once.

        @return Promise for a dict of Luncho data of all countries.
        '''

        if self.allLunchoDatasExpiration > time.time():
            return self.lunchoDataCache

        self.lunchoDataCache = self.lunchoApi.all_luncho_data(**kwargs)
        assert self.lunchoDataCache
        assert self.lunchoDataCache['JP']
        self.allLunchoDatasExpiration = self.lunchoDataCache['JP'].expiration
        self.exchangeRatesCache = {}
        return self.lunchoDataCache


    def get_country_code(self, **kwargs) -> str:
        '''
         Returns an estimated country code with IP address. Available only if the server supports.
        '''

        if self.countryCodeCache:
            return self.countryCodeCache

        self.countryCodeCache = self.lunchoApi.country_code(**kwargs)
        return self.countryCodeCache

    def get_exchange_rates(self) -> Dict[CurrencyCode, float]:
        '''
        Returns a dict of currency code to USD based exchange rate of all supported
        countries such as {'USD': 1.0, 'JPY' : 0.94, 'expiration': 1726553240.844584 ...}.

        The key 'expiration' contains expiration time in UTC in float.

         @return a dict of currency code to USD based exchange rate of all supported countries. {currency code: USD based exchange rate}
        '''

        lunchoData: LunchoData

        if self.exchangeRatesCache:
            return self.exchangeRatesCache

        self.get_all_luncho_data()

        self.exchangeRatesCache = {}
        for lunchoData in self.lunchoDataCache.values():
            self.exchangeRatesCache[lunchoData.currency_code] = lunchoData.exchange_rate

        # save expiration
        self.exchangeRatesCache['expiration'] = self.lunchoDataCache['JP'].expiration

        return self.exchangeRatesCache


    def __getattr__(self, method_name):
        ''' Delegates all other methods to self.lunchoApi. '''

        def method(*args, **kwargs):
            return getattr(self.lunchoApi, method_name)(*args, **kwargs)
        return method
