'''
  Luncho inflation ratio

  See for detail:  https://luncho-de-peace.org/about#data

  @author HIRANO Satoshi
  @since  2024/09/25


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
from src import data_loader, ppp_data
from src.types import CurrencyCode, CountryCode, Country

# class InflationRatioType(TypedDict, total=False):
#     country_code: CountryCode   # country code
#     ratios: dict[int, float]    # year and inflation ratio
#InflationRatio: InflationRatioType = {}

InflationRatio: dict[str, dict[int, float]] = {}

def load_inflation_ratio(force_download: bool = False, use_dummy_data: bool = False) -> None:
    def process_inflation_ratio(data: dict[str, Any]|None, source: str) -> bool:
        '''
          Args:
             data:
                 {"values":{"PCPIPCH":{"JPN":{
                       "1980":7.79999999999999982236431605997495353221893310546875,
                       "1981":4.9000000000000003552713678800500929355621337890625,
        '''

        year_str_infl: dict[str, float]   # {"1980": 2.44, "1981": 2.45...}
        year_infl: dict[int, float]       # 1980: 2.44, 1981: 2.45...}
        country_code: str                 # ISO 2 letter code  'JP'
        country_code3: str                # ISO 3166 Alpha 3 code 'JPN'

        if not data:
            if InflationRatio:
                logging.info('Reusing existing inflation ratio in InflationRatio.')
                return True
            assert False, 'Inflation ratio data is not available. Abort.'

        for country_code3, year_str_infl in data['values']['PCPIPCH'].items():
            country_code: str = conf.IMF_Country_Code_Fix.get(country_code3) or pycountry_convert.country_alpha3_to_country_alpha2(country_code3)
            if country_code != "??":
                InflationRatio[country_code] = {int(year): value for year, value in year_str_infl.items()}

        logging.info(f"Loaded {len(InflationRatio)} inflation ratio data from {source}.")
        return True

    data_loader.load_data(conf.INFLATION_RATIO_API, conf.INFLATION_RATIO_FILE, process_inflation_ratio)
    update_dollar_per_luncho_in_Countries()

def update_dollar_per_luncho_in_Countries() -> None:
    ''' Update dollar per Luncho in Countries to reflect the latest inflation ratio. '''

    from src import exchange_rate  #pylint: disable=import-outside-toplevel
    logging.info('ppp_data.update_exchange_rate_in_Countries()')

    conf.This_Year = datetime.datetime.today().year
    conf.Dollar_Per_Luncho = calc_dollar_per_luncho(conf.This_Year)

    with exchange_rate.global_variable_lock:
        for _country_code, country in ppp_data.Countries.items():
            country.dollar_per_luncho = conf.Dollar_Per_Luncho

def calc_dollar_per_luncho(target_year: int) -> float:
    ''' Calculate dollar per luncho value for the year. '''

    dollar_per_luncho: float = conf.Base_Dollar_Per_Luncho

    if target_year >= conf.Base_Dollar_Per_Luncho_Year:
        for year in range(conf.Base_Dollar_Per_Luncho_Year, target_year + 1):
            ratio: float = InflationRatio['US'].get(year, 1.0) # 3.4%
            dollar_per_luncho *= 1.0 + ratio * 0.01           # 3.4 -> 103.4
            logging.info(f'Inflation ratio in {year} is {ratio}. 100 Luncho is {dollar_per_luncho * 100}.')
    else:
        for year in range(conf.Base_Dollar_Per_Luncho_Year, target_year + 1):
            ratio: float = InflationRatio['US'].get(year, 1.0) # 3.4%
            dollar_per_luncho /= 1.0 + ratio * 0.01           # 3.4 -> 103.4
            logging.info(f'Inflation ratio in {year} is {ratio}. 100 Luncho is {dollar_per_luncho * 100}.')

    return dollar_per_luncho

def cron_thread(use_dummy_data: bool=False):
    ''' The cron thread. Update exchange rate data at 00:06 UTC everyday,
       since exchangerate.host updates at 00:05. https://exchangerate.host/#/#docs"

        In case on App Engine, cron.yaml is used and this is not used.
    '''

    while True:
        time.sleep(time_to_update() - time.time())
        #time.sleep(10)        # test

        load_inflation_ratio(use_dummy_data)


def time_to_update() -> float:
    ''' Returns next update time in UTC time. We update at 00:04 everyday. '''

    now: datetime.datetime = datetime.datetime.now()
    tomorrow: datetime.datetime  = now + datetime.timedelta(days=1)
    time_until_midnight: datetime.timedelta = datetime.datetime.combine(tomorrow, datetime.time.min) - now
    seconds_until_midnight: int = time_until_midnight.seconds
    result_time = time.time() + seconds_until_midnight + 4*60

    return result_time
