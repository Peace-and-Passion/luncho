'''
  Luncho PPP data

  See for detail:  https://luncho-de-peace.org/about#data

  @author HIRANO Satoshi
  @since  2021/05/13


'''

import csv
import datetime
import logging
import re
import time
from typing import cast, Any, TypedDict

import pycountry
import pycountry_convert
from google.cloud import storage

import conf
from conf import Dollar_PER_LUNCHO
from src import data_loader
from src.types import CurrencyCode, CountryCode, Country



Countries: dict[CountryCode, Country] = {}      # A map of country data
CountryCode_Names: dict[CountryCode, str] = {}  # A map of country code and name

# ICP country metadata
#   {'AFG': { 'Code': 'AFG', 'Long NameError(Islamic State of Afghanistan,AFN: Afghani,Afghanistan,
#   {'ALB': {1980: 24.4, 1981: 24.5...
class CountryMetadataType(TypedDict):
    ''' Country metadata file type specified with ICP_FILE. '''

    code: CountryCode         # AF  (ISO 2 letter country code)
    name: str                 # Afghanistan (common name in pycountry)
    long_name: str            # Islamic State of Afghanistan (not used)
    currency_code: CurrencyCode  # AFN  (ISO 3 letter currency code)
    currency_name: str        # Afghani
    table_name: str           # Afghanistan
    coverage: str | None   # Urban and Rural, Urban only, Rural only

Country_Metadata: dict[CountryCode, CountryMetadataType] = {}   # country_code, CountryMetadataType

kosovo = pycountry.db.Data()
kosovo.alpha_2 = "XK"
kosovo.alpha_3 = "KSV"
kosovo.name = "Kosovo"
kosovo.numeric = "383"
kosovo.official_name = "Kosovo"


def load_metadata() -> None:
    '''  Loads country metadata from data/Data_Extract_From_ICP_2017_Metadata.csv.
    '''

    def process_one_country(data: Any) -> None:
        ''' Process a country metadata and put it in the Country_Metadata map.

         ICP_FILE contains for countries and regions as following.

          ITA,Italian Republic,EUR: Euro,Italy,Capital-city only
          JAM,Jamaica,JMD: Jamaican Dollar,Jamaica,...
          JPN,Japan,JPY: Yen,Japan,Capital-city only

        '''

        global Country_Metadata
        country_data: Any
        country_code: str                     # ISO 2 letter code
        country_code3: str = data['Code']     # ISO 3 letter code
        del data['Code']

        if country_code3 == 'BON': # bonaire, but not found in IMF PPP data
            country_code3 = 'BES'
        if country_code3 == 'KSV': # Kosovo is not found in pycountry but in IMF PPP data
            country_data = kosovo
        else:
            country_data = pycountry.countries.get(alpha_3=country_code3)
        if country_data:
            country_code = data['country_code'] = country_data.alpha_2
            data['name'] = getattr(country_data, 'common_name', country_data.name)
            del data['Long Name']

            # decompose Currency Unit           AFN: Afghani (2011)
            currency_unit: str = data['Currency Unit']
            data['currency_code'] = currency_unit[0:3]
            data['currency_name'] = re.sub(' \\(.*?\\)', '', currency_unit[5:])
            del data['Currency Unit']

            Country_Metadata[country_code] = cast(CountryMetadataType, dict(data))
            #print(str(Country_Metadata))
        else:
            print("No location information on IP address: " + country_code3)
            #error(country_code3, "No location information on IP address")

    for file in ('data/' + conf.ICP_FILE, 'data/Data_Extract_From_ICP_Fix.csv'):
        with open(file, newline='', encoding="utf_8_sig") as metadata_file:
            metadata_reader  = csv.DictReader(metadata_file)

            for data in metadata_reader:
                process_one_country(data)

def load_ppp_data(force_download: bool = False, use_dummy_data: bool = False) -> None:
    def process_ppp_data(ppp_data: dict[str, Any]|None, from_location: str) -> bool:

        year_str_ppp: dict[str, float]    # {"1980": 2.44, "1981": 2.45...}
        year_ppp: dict[int, float]        # 1980: 2.44, 1981: 2.45...}
        country_code: str                 # ISO 2 letter code  'JP'
        country_code3: str                # ISO 3166 Alpha 3 code 'JPN'

        if not ppp_data:
            if Countries:
                logging.info('Reusing existing PPP data in Countries.')
                return
            assert False, 'PPP rate data is not available. Abort.'

        country_code_fix_map = { 'UVK': kosovo.alpha_2, # Kosovo
                                 'WBG': 'PS' }   #  West Bank and Gaza, PSE
        for country_code3, year_str_ppp in ppp_data['values']['PPPEX'].items():
            country_code: str = country_code_fix_map.get(country_code3) or pycountry_convert.country_alpha3_to_country_alpha2(country_code3)
            if country_code == 'SS':   # skip South Sudan since its PPP is too large to the graph
                year_ppp = {}
            else:
                year_ppp = {int(year): value for year, value in year_str_ppp.items()}

            # if country_code == 'WBG':   # Gaza -> Palestine
            #     country_code = 'PSE'
            if country_code in ('TL', 'KOR'): # Timor-Leste and North Korea are in Asia.  TL, KP
                continent_code = 'AS'
            else:
                continent_code = pycountry_convert.country_alpha2_to_continent_code(country_code)

            Countries[country_code] = Country(
                year_ppp = year_ppp,
                country_code = country_code,
                currency_code = Country_Metadata[country_code]['currency_code'],
                continent_code = continent_code,
                currency_name = Country_Metadata[country_code]['currency_name'],
                country_name = Country_Metadata[country_code]['name'],
            )
            CountryCode_Names[country_code] = Country_Metadata[country_code]['name']

        logging.info(f"Loaded {len(Countries)} PPP data from {from_location}.")
        return True

    data_loader.load_data(conf.PPP_API, conf.PPP_FILE, process_ppp_data)

def update_exchange_rate_in_Countries() -> None:
    ''' Update Countries to reflect the latest exchange rates. '''

    from src import exchange_rate  #pylint: disable=import-outside-toplevel
    year: int = datetime.datetime.today().year
    logging.info('ppp_data.update_exchange_rate_in_Countries()')

    with exchange_rate.global_variable_lock:
        for _country_code, country in Countries.items():
            country.ppp = country.year_ppp.get(year, 0.0) if country.year_ppp else None # country's ppp of this year
            country.exchange_rate = exchange_rate.exchange_rate_per_USD(country.currency_code)
            country.dollar_per_luncho = conf.Dollar_PER_LUNCHO
            country.expiration = exchange_rate.expiration

def cron_thread(use_dummy_data: bool=False):
    ''' The cron thread. Update exchange rate data at 00:06 UTC everyday,
       since exchangerate.host updates at 00:05. https://exchangerate.host/#/#docs"

        In case on App Engine, cron.yaml is used and this is not used.
    '''

    while True:
        time.sleep(time_to_update() - time.time())
        #time.sleep(10)        # test
        load_ppp_data(use_dummy_data)


def time_to_update() -> float:
    ''' Returns next update time in UTC time. We update at 00:04 everyday. '''

    now: datetime.datetime = datetime.datetime.now()
    tomorrow: datetime.datetime  = now + datetime.timedelta(days=1)
    time_until_midnight: datetime.timedelta = datetime.datetime.combine(tomorrow, datetime.time.min) - now
    seconds_until_midnight: int = time_until_midnight.seconds
    result_time = time.time() + seconds_until_midnight + 4*60

    return result_time

load_metadata()
