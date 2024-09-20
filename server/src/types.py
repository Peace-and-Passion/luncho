'''
  Types

  Created on 2021/05/12

  Author: HIRANO Satoshi
'''

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

CountryCode = str     # ISO 3166-1 2 letter code. E.g. 'JP'
CurrencyCode = str    # ISO 4217   3 letter currency code. E.g. 'AFN'
ContinentCode = str   # NA, SA, AS, OC, AF
C1000 = 1000

continents: dict[ContinentCode, str] = {
    'NA': 'North America',
    'SA': 'South America',
    'EU': 'Europe',
    'AS': 'Asia',
    'OC': 'Australia',
    'AF': 'Africa',
}

class LunchoData(BaseModel):   #pylint: disable=too-few-public-methods
    ''' Data needed to convert between Luncho and local currency.
        If data for the country is not available, either ppp or exchange_rate is 0.
    '''

    country_code: CountryCode       # Country code
    country_name: str               # Country name
    continent_code: str             # Continent

    currency_code: CurrencyCode     # Currency code
    currency_name: str              # Currency name
    exchange_rate: Optional[float] = None # Exchange rate per US Dollar. 0 if not available.
    #dollar_value: float             # US Dollar value of the luncho
    ppp: Optional[float] = None           # PPP value. 0 if not available.
    dollar_per_luncho: Optional[float] = None # dollar/luncho rate
    expiration: Optional[float] = None   # Data expiration in unix time. You need to call APIs after this time.
    #dollar_value: float
    #local_currency_value: float

class Country(LunchoData):   #pylint: disable=too-few-public-methods
    ''' Internal data with yearly PPP values. '''
    year_ppp: Optional[dict[int, float]] = None  # { year: ppp }  Optional

# class CountryCodeName(BaseModel):
#     ''' Country code and name. '''

#     country_code: CountryCode       # Country code
#     country_name: str               # Country name


class Currency():   #pylint: disable=too-few-public-methods
    """
    NOT USED. Currency. Value is multipied by 1000.

    """

    def __init__(self, value=None, code=None, unit=None,):
        super().__init__()
        self.value = value
        self.code = code
        self.unit = unit
