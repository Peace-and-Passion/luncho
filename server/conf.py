'''
  Configuration of the Luncho server

  @author HIRANO Satoshi
  @since 2021/05/12
'''

from __future__ import annotations
import os

# Configurable constants
PRODUCTION: bool          = os.environ.get('PRODUCTION', 'False') in ('True', 'true')  # NOT USED
GCS_BUCKET: str | None    = os.environ.get('GCS_BUCKET', None)
FOREX_API_KEY: str        = os.environ.get('FOREX_API_KEY', 'Set_your_API_key_to__FOREX_API_KEY__environment_variable.')
FOREX_HOURLY_UPDATE       = False   # True to fetch forex date hourly, False for daily
IS_APPENGINE              = os.environ.get('GAE_APPLICATION') is not None  # True if running on Google App Engine

EXCHANGERATE_URL         = 'https://openexchangerates.org/api/latest.json?app_id='
#EXCHANGERATE_URL        = 'https://exchangerate.host/api/latest?access_key='
#EXCHANGERATE_URL        = 'http://data.fixer.io/api/latest?access_key='

def Header_To_Fetch(lang: str) -> dict:
    return {"Accept-Language": "".join([lang, ";"]), "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}


# Unconfigurable constants

# Luncho: Caution! This will be changed to take inflation into account automatically.
Dollar_PER_LUNCHO: float     = 17.0/100.0      # 100 Luncho is $17 USD.
API_V1_STR: str = "/v1"

#
# exchange rates
#
EXCHANGE_RATE_FILE         = 'exchange-rate-backup.json'
DUMMY_FIXER_EXCHANGE_FILE  = 'data/dummy-fixer-exchange-2020-11-11.json'

#
# PPP from IMF API
#
PPP_API   = 'https://www.imf.org/external/datamapper/api/v1/PPPEX'  # for all countries and all periods
PPP_FILE  = 'ppp-data-backup.json'
ICP_FILE  = 'Data_Extract_From_ICP_2017_Metadata.csv'

# Luncho client library languages
#  'language': 'option'
#
#  Set some from https://openapi-generator.tech/docs/generators
#
Gen_Openapi: dict[str, str] = {
    # add library=asyncio if needed, otherwise it uses default (library=urllib3)
    'python': 'packageName=luncho_python,projectName=luncho_python',
    'typescript-fetch': 'supportsES6=true,npmName=luncho-typescript-fetch,withoutRuntimeChecks=true',
    #'typescript-aurelia': 'supportsES6=true,npmName=luncho_typescript-aurelia',
}
Openapi_Schema_File = 'data/openapi_schema.json'
