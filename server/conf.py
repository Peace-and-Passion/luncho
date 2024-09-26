'''
  Configuration of the Luncho server

  @author HIRANO Satoshi
  @since 2021/05/12
'''

import datetime
import json5
import os

# Configurable constants
PRODUCTION: bool          = os.environ.get('PRODUCTION', 'False') in ('True', 'true')  # NOT USED
GCS_BUCKET: str | None    = os.environ.get('GCS_BUCKET', None)
FOREX_API_KEY: str        = os.environ.get('FOREX_API_KEY', 'Set_your_API_key_to__FOREX_API_KEY__environment_variable.')
FOREX_HOURLY_UPDATE       = False   # True to fetch forex date hourly, False for daily
IS_APPENGINE              = os.environ.get('GAE_APPLICATION') is not None  # True if running on Google App Engine

EXCHANGE_RATE_URL         = 'https://openexchangerates.org/api/latest.json?app_id='
#EXCHANGE_RATE_URL        = 'https://exchangerate.host/api/latest?access_key='
#EXCHANGE_RATE_URL        = 'http://data.fixer.io/api/latest?access_key='

def Header_To_Fetch(lang: str) -> dict:
    return {"Accept-Language": "".join([lang, ";"]), "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}

Top_Dir = os.path.dirname(os.path.abspath(__file__))
IMF_Country_Code_Fix: dict[str, str]   # fix map for IMF country code
with open(os.path.join(Top_Dir, 'data/IMF_country_code_fix.json'), newline='', encoding="utf_8_sig") as fix_file:
    IMF_Country_Code_Fix = json5.load(fix_file)


# Unconfigurable constants
This_Year: int = datetime.datetime.today().year

# definition of Luncho
Dollar_Per_Luncho: float          = 0               # dollar per Luncho in this year
Base_Dollar_Per_Luncho: float     = 12.2/100.0      # base dollar per Luncho in the base year
Base_Dollar_Per_Luncho_Year: int  = 2019            # base year of dollar per Luncho
# Base_Dollar_Per_Luncho: float  = 3.45/100.0      # base dollar per Luncho in the base year
# Base_Dollar_Per_Luncho_Year: int  = 1980            # base year of dollar per Luncho

#
# exchange rates
#
EXCHANGE_RATE_FILE         = 'data/backup-exchange-rate.json'
EXCHANGE_RATE_TEST_FILE    = 'data/test-data-exchange-rate-2024-09-26.json'
#EXCHANGE_RATE_TEST_FILE   = 'data/test-data-fixer-exchange-2020-11-11.json'

#
# PPP data from IMF API
#
PPP_DATA_URL              = 'https://www.imf.org/external/datamapper/api/v1/PPPEX'  # for all countries and all periods
INFLATION_RATIO_API       = 'https://www.imf.org/external/datamapper/api/v1/PCPIPCH/USA' # inflation ratio of average in the period
PPP_DATA_FILE             = 'data/backup-ppp-data.json'
PPP_DATA_TEST_FILE        = 'data/test-data-ppp-data-2024-09-26.json'
INFLATION_RATIO_FILE      = 'data/backup-inflation-ratio.json'
INFLATION_RATIO_TEST_FILE = 'data/test-data-inflation-ratio-2024-09-26.json'
ICP_METADATA_FILE         = 'data/Data_Extract_From_ICP_2017_Metadata.csv'
ICP_METADATA_FIX_FILE     = 'data/Data_Extract_From_ICP_Fix.csv'

#
# Luncho API
#
API_V1_STR: str = "/v1"

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
