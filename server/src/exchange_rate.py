'''
  Exchange rates

  Created on 2021/05/09

  Author: HIRANO Satoshi
'''

from __future__ import annotations
import datetime
import json
import time
import logging
import threading
from typing import TypedDict, Any, cast

from src import data_loader
from src.types import CurrencyCode
import conf

global_variable_lock = threading.Lock()

# exchange rates based on USD
Exchange_Rates: dict[CurrencyCode, float] = {}  # { currencyCode: rate }

# Expiration time of Exchange_Rates
expiration: float = 0.0

# time of the last load of Exchange_Rates
last_load: float = 0

class FixerExchangeRate(TypedDict):
    ''' Exchange rate struct returned by Fixer API. '''

    rates: dict[CurrencyCode, float]   # { "AED": 4.337445, ...}
    timestamp: int   # 1605081845
    base: str        # "USD" if openexchangerates.org, "EUR" if fixer.io and exchangerate.host
    #success: bool   # true if API success. none from openexchangerates.org
    #date: str       #"2020-11-11", none from openexchangerates.org

def exchange_rate_per_USD(currencyCode: CurrencyCode) -> float: #pylint: disable=invalid-name
    ''' Returns exchange rate per USD for the currencyCode.
        None if the currencyCode is not available. '''

    return Exchange_Rates.get(currencyCode, 0.0)


def load_exchange_rates(use_dummy_data: bool):
    ''' Load exchange rates from a forex API or saved rate data from GCS.

      Test:
        pytest test/test_server.py::test_server_api_error
    '''

    def process_exchange_rate(data: dict[str, Any]|None, from_location: str) -> bool:
        global Exchange_Rates, last_load, expiration
        fixer_exchange_rate: FixerExchangeRate = cast(FixerExchangeRate, dict)

        if not data:
            if Exchange_Rates:
                logging.info('Reusing existing exchage rates.')
                return True
            assert False, 'Exchange rate data is not available. Abort.'

        # 160 is for an incident occured in 2023 that lacks many currencies
        if not fixer_exchange_rate.get('rates') or len(fixer_exchange_rate.get('rates')) < 160:
            logging.info(f"Too few exchange rates ({len(fixer_exchange_rate.get('rates'))}) fetched.")
            return False

        # if base is not USD, convert rates into USD. fixer returns in EUR
        if fixer_exchange_rate.get('base') != 'USD':
            new_exchange_rates: dict[CurrencyCode, float] = {}
            usd: float = fixer_exchange_rate['rates']['USD']  # USD per euro
            for currecy_code, euro_value in fixer_exchange_rate['rates'].items():
                new_exchange_rates[currecy_code] = euro_value / usd   # store in USD
            fixer_exchange_rate['rates'] = new_exchange_rates

        with global_variable_lock:
            Exchange_Rates = fixer_exchange_rate.get('rates')
            last_load = time.time()
            expiration = time_to_update() + 40  # expires 40 sec after Forex data update time

        logging.info(f"Loaded {len(Exchange_Rates)} exchange rate data from {from_location}.")
        return True

    if use_dummy_data:
        with open(conf.DUMMY_FIXER_EXCHANGE_FILE, 'r', newline='', encoding="utf_8_sig") as fixer_file:
            fixer_exchange_rate = json.load(fixer_file) # 168 currencies
        process_exchange_rate(fixer_exchange_rate, 'dummy file')
    else:
        data_loader.load_data(conf.EXCHANGERATE_URL + conf.FOREX_API_KEY, conf.EXCHANGE_RATE_FILE, process_exchange_rate)

    from src import ppp_data
    ppp_data.update_exchange_rate_in_Countries()

def cron_thread(use_dummy_data):
    ''' The cron thread. Update exchange rate data at 00:06 UTC everyday,
       since exchangerate.host updates at 00:05. https://exchangerate.host/#/#docs"

        In case on App Engine, cron.yaml is used and this is not used.
    '''

    while True:
        time.sleep(time_to_update() - time.time())
        #time.sleep(10)        # test
        load_exchange_rates(use_dummy_data)

def time_to_update() -> float:
    ''' Returns next update time in POSIX time. '''
    now: datetime.datetime

    if conf.FOREX_HOURLY_UPDATE:
        # Fixer updates every hour. We update 3 minute every hour. 00:03, 01:03, 02:03...
        #
        #  now = datetime.datetime(2021, 5, 21, 15, 26, 27, 291409)
        #  next_hour = datetime.datetime(2021, 5, 21, 16, 26, 27, 291409)
        #  time_until_next_hour = datetime.timedelta(seconds=2012, microseconds=708591)
        #  seconds_until_next_hour = 2012
        #  time_to_update = 1621580600 (2021-05-21 16:03)
        #
        now = datetime.datetime.now()
        next_hour: datetime.datetime  = now + datetime.timedelta(hours=1)
        time_until_next_hour: datetime.timedelta = next_hour.replace(minute=0, second=0, microsecond=0) - now
        seconds_until_next_hour: int = time_until_next_hour.seconds
        result_time: float = time.time() + seconds_until_next_hour + 3*60
        return result_time

    # we update at 00:06 everyday.
    now = datetime.datetime.now()
    tomorrow: datetime.datetime  = now + datetime.timedelta(days=1)
    time_until_midnight: datetime.timedelta = datetime.datetime.combine(tomorrow, datetime.time.min) - now
    seconds_until_midnight: int = time_until_midnight.seconds
    result_time = time.time() + seconds_until_midnight + 6*60
    return result_time
