'''
  Luncho API

  @author HIRANO Satoshi
  @date  2021/05/13
'''

from typing import Optional, cast

from fastapi import Header, APIRouter
from fastapi_utils.openapi import simplify_operation_ids

from src import exchange_rate
from src.utils import error
from src.ppp_data import Countries, CountryCode_Names
from src.types import CountryCode, LunchoData, Country

api_router = APIRouter()

@api_router.get("/luncho-data", response_model=LunchoData, tags=['Luncho'])
async def luncho_data(
        country_code: CountryCode, # client provided country code in ISO-3166-1-2 formant like 'JP'
        #pylint: disable=redefined-outer-name
) -> LunchoData:
    '''
      Returns LunchoData that is needed to convert between Luncho and local currency of the countryCode.
        If data for the country is not available either ppp or exchange_rate is 0.
      Data size is about 400 bytes.

      - **country_code**: client provided country code in ISO-3166-1-2 formant like 'JP'
      - **return**: LunchoData

    '''
    country: Country | None = Countries.get(country_code, None)
    if not country:
        error(country_code, 'Invalid country code')
        # never come here

    return cast(LunchoData, country)

@api_router.get("/country-code", response_model=str, tags=['Luncho'])
async def country_code(
        X_Appengine_Country: Optional[str]=Header(None),  # country code if on Google App Engine
        #pylint: disable=invalid-name
) -> str:
    '''
      Returns country code. This is available only when the server runs on Google App Engine.
      - **X_Appengine_Country**: Internal use. Ignore this.
      - **return**: str. A country code.

    '''
    print('X_Appengine_Country = [' + str(X_Appengine_Country) + ']')
    return X_Appengine_Country or 'JP'

@api_router.get("/countries", response_model=dict[CountryCode, str], tags=['Luncho'])
async def countries() -> dict[CountryCode, str]:
    '''
      Returns a dict of supported country codes and names so that you can show
    a dropdown list of countries. Data size is about 3.5KB.
       E.g. {'JP': 'Japan', 'US': 'United States'...}.
        If data for a country is not available, either its ppp or exchange_rate is 0.

      - **return**: dict[CountryCode, str] A dict of a country code and country name.
    '''
    return CountryCode_Names


@api_router.get("/all-luncho-data", response_model=dict[CountryCode, LunchoData], tags=['Luncho'])
async def all_luncho_data() -> dict[CountryCode, LunchoData]:
    '''
      Returns A dict of LunchoDatas for supported countries. Data size is about 40KB.
    - **return**: dict[CountryCode, LunchoData] A dict of a country code and LunchoData.
    '''

    return Countries


@api_router.get("/health", tags=['Luncho'])
async def health() -> None:
    '''
      Do nothing other than telling it's OK.
    '''
    return


@api_router.get("/update_exchange_rate", include_in_schema=False)  # not in OpenAPI
async def update_exchange_rate() -> None:
    '''
      Update exchange rate data. This is an internal API.
    '''
    exchange_rate.load_exchange_rates(False)


# use method names in OpenAPI operationIds to generate methods with the method names
simplify_operation_ids(api_router)
