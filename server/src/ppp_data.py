'''
  Luncho PPP data

  See for detail:  https://luncho-de-peace.org/about#data

  @author HIRANO Satoshi
  @since  2021/05/13


'''

from __future__ import annotations
import csv
import datetime
import json
import logging
import os
import re
import time
import urllib.request
import urllib.error
from typing import cast, Any, TypedDict
import pycountry
import pycountry_convert

from google.cloud import storage

import conf
from conf import SDR_PER_LUNCHO
from src.types import CurrencyCode, CountryCode, Country

PPP_FILE  = 'data/imf-dm-export-20221225.csv'
ICP_FILE  = 'data/Data_Extract_From_ICP_2017_Metadata.csv'


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

    for file in (ICP_FILE, 'data/Data_Extract_From_ICP_Fix.csv'):
        with open(file, newline='', encoding="utf_8_sig") as metadata_file:
            metadata_reader  = csv.DictReader(metadata_file)

            for data in metadata_reader:
                process_one_country(data)


def load_ppp_data(force_download: bool = False, use_dummy_data: bool = False) -> None:
    ''' Loads PPP data from IMF API into Countries.

       Args:
          force_download:  Force to download with IMF API.
          use_dummy_data:  True to use dummy data file.
    '''

    global Country_Metadata, Countries, CountryCode_Names
    logging.info('ppp_data.load_ppp_data()')

    def parse_ppp_data(ppp_data: dict) -> None:

        year_str_ppp: dict[str, float]    # {"1980": 2.44, "1981": 2.45...}
        year_ppp: dict[int, float]        # 1980: 2.44, 1981: 2.45...}
        country_code: str                 # ISO 2 letter code  'JP'
        country_code3: str                # ISO 3166 Alpha 3 code 'JPN'

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

    # first, we try the saved PPP data in GCS or file if it has today's timestamp
    ppp_data_saved: dict|None = download_ppp_data()

    if ppp_data_saved and not force_download:
        timestamp: float = ppp_data_saved.get('timestamp', 0)
        timestamp_date: datetime.date = datetime.datetime.utcfromtimestamp(timestamp).date()
        if datetime.datetime.utcnow().date() == timestamp_date:  # today?
            parse_ppp_data(ppp_data_saved)
            logging.info(f"Loaded {len(ppp_data_saved['values']['PPPEX'])} PPP data from backup file")
            return

    # not today's data. let's download PPP data with IMF API.
    # a big thank you to all contributors to the data!
    try:
        with urllib.request.urlopen(conf.PPP_API) as return_data:
            ppp_data_fetched = json.loads(return_data.read())
            assert ppp_data_fetched

            ppp_data_fetched['timestamp'] = time.time()
            backup_ppp_data(ppp_data_fetched)             # save it with timestamp for the next time
            parse_ppp_data(ppp_data_fetched)              # parse and store it
            logging.info(f"Fetched {len(ppp_data_fetched['values']['PPPEX'])} PPP data from IMF")

    except urllib.error.URLError as ex:
        # network error! we use the last PPP data instead.
        if ppp_data_saved:
            logging.warn('Failed to fetch PPP data from %s, falling down to the last data: %s ', conf.PPP_API, str(ex))
            parse_ppp_data(ppp_data_saved)
        else:
            logging.error('Failed to fetch PPP data from %s, give up: %s ', conf.PPP_API, str(ex))


def update_exchange_rate_in_Countries() -> None:
    ''' Update Countries to reflect the latest exchange rates. '''

    from src import exchange_rate  #pylint: disable=import-outside-toplevel
    year: int = datetime.datetime.today().year
    logging.info('ppp_data.update_exchange_rate_in_Countries()')

    with exchange_rate.global_variable_lock:
        for _country_code, country in Countries.items():
            country.ppp = country.year_ppp.get(year, 0.0) if country.year_ppp else None # country's ppp of this year
            country.exchange_rate = exchange_rate.exchange_rate_per_USD(country.currency_code)
            country.dollar_per_luncho = SDR_PER_LUNCHO / exchange_rate.SDR_Per_Dollar
            country.expiration = exchange_rate.expiration

            # country['ppp'] = country['year_ppp'].get(year, 0.0)  # country's ppp of this year
            # country['exchange_rate'] = exchange_rate.exchange_rate_per_USD(country['currency_code'])
            # country['dollar_per_luncho'] = SDR_PER_LUNCHO / exchange_rate.SDR_Per_Dollar
            # country['expiration'] = exchange_rate.expiration

def backup_ppp_data(ppp_data: dict) -> None:
    """ Backup PPP data to GCS or the file.

    Args:
       ppp_data: A dict that format is the same as PPP data got from IMF API.
    """

    if conf.GCS_BUCKET:
        storage.Client().bucket(conf.GCS_BUCKET).blob(conf.PPP_FILE).upload_from_string(json.dumps(ppp_data))
    else:
        with open('data/' + conf.PPP_FILE, 'w', newline='', encoding="utf_8_sig") as ppp_data_file:
            ppp_data_file.write(json.dumps(ppp_data))


def download_ppp_data() -> dict | None:
    """ Downloads PPP data from GCS or the file.

    Returns: A dict that format is the same as PPP data got from IMF API.

    """

    if conf.GCS_BUCKET:
        try:
            return json.loads(storage.Client().bucket(conf.GCS_BUCKET).blob(conf.PPP_FILE).download_as_string())
        except Exception as ex:
            logging.warn('Failed to download saved PPP file from GCS bucket %s: %s ', conf.GCS_BUCKET, str(ex))

    try:
        with open('data/' + conf.PPP_FILE, newline='', encoding="utf_8_sig") as ppp_data_file:
            return json.load(ppp_data_file)
    except Exception as ex:
        logging.error('Failed to open saved PPP file from %s: %s ', 'data/' + conf.PPP_FILE, str(ex))

    return None


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
