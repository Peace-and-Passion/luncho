'''
  Exchange rates

  Created on 2021/05/09

  Author: HIRANO Satoshi
'''

from __future__ import annotations
import datetime
import http
import json
import time
import logging
import threading
import urllib.request
import urllib.error
from typing import TypedDict

from google.cloud import storage

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

    global Exchange_Rates, last_load, expiration
    fixer_exchange_rate: FixerExchangeRate = {}
    success: bool = False
    err_msg: str = ''

    if use_dummy_data:
        with open(conf.DUMMY_FIXER_EXCHANGE_FILE, 'r', newline='', encoding="utf_8_sig") as fixer_file:
            fixer_exchange_rate = json.load(fixer_file) # 168 currencies
    else:
        # try API URLs that are Fixer compatible
        for api_url in conf.EXCHANGERATE_URLS:
            url = api_url + (conf.FOREX_API_KEY or '')
            request =  urllib.request.Request(url, headers=conf.Header_To_Fetch('en'))

            try:
                with urllib.request.urlopen(request) as return_data:
                    fixer_exchange_rate = json.loads(return_data.read())

                    # 160 is for an incident occured in 2023 that lacks many currencies
                    if fixer_exchange_rate.get('rates') and len(fixer_exchange_rate.get('rates')) > 160:
                        logging.info(f"Fetched {len(fixer_exchange_rate.get('rates'))} exchange rates from {api_url}")

                    # if base is not USD, convert rates into USD. fixer returns in EUR
                    if fixer_exchange_rate.get('base') != 'USD':
                        new_exchange_rates: dict[CurrencyCode, float] = {}
                        usd: float = fixer_exchange_rate['rates']['USD']  # USD per euro
                        for currecy_code, euro_value in fixer_exchange_rate['rates'].items():
                            new_exchange_rates[currecy_code] = euro_value / usd   # store in USD
                        fixer_exchange_rate['rates'] = new_exchange_rates

                    # save it for emergency
                    upload_exchange_rate(fixer_exchange_rate)
                    success = True
                    break

            except urllib.error.URLError as ex:
                err_msg = str(ex)

        if not success:
            logging.warn('Failed to fetch exchange rates from %s, falling down to the last data: %s ', conf.EXCHANGERATE_URLS, err_msg)

            # reuse existing data if there is
            if Exchange_Rates:
                logging.info('Reuse existing exchage rates')
                return

            # download saved data
            rates: FixerExchangeRate | None = download_exchange_rate()
            if rates:
                fixer_exchange_rate = rates
                logging.info('Use saved exchage rates')
            else:
                raise Exception('Failed to fetch exchange rates either from API and save data') #pylint: disable=broad-exception-raised

    # update globals
    with global_variable_lock:
        Exchange_Rates = fixer_exchange_rate.get('rates')
        last_load = time.time()
        expiration = time_to_update() + 40  # expires 40 sec after Forex data update time

    # update PPP data
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


def upload_exchange_rate(exchange_rate: FixerExchangeRate) -> None:
    """ Uploads exchange rate data to GCS."""

    if conf.GCS_BUCKET:
        storage.Client().bucket(conf.GCS_BUCKET).blob(conf.EXCHANGE_RATE_FILE).upload_from_string(json.dumps(exchange_rate))
    else:
        with open('data/' + conf.EXCHANGE_RATE_FILE, 'w', newline='', encoding="utf_8_sig") as fixer_new_file:
            fixer_new_file.write(json.dumps(exchange_rate))

def download_exchange_rate() -> FixerExchangeRate | None:
    """ Downloads exchange rate data from GCS."""

    if conf.GCS_BUCKET:
        try:
            blob = storage.Client().bucket(conf.GCS_BUCKET).blob(conf.EXCHANGE_RATE_FILE)
            return json.loads(blob.download_as_string())
        except Exception as ex:
            logging.warn('Failed to download saved exchange rate from GCS bucker %s: %s ', conf.GCS_BUCKET, str(ex))

    try:
        with open('data/' + conf.EXCHANGE_RATE_FILE, newline='', encoding="utf_8_sig") as fixer_last_file:
            return json.load(fixer_last_file)
    except Exception as ex:
        logging.error('Failed to open exchange rate backup file from %s: %s ', 'data/' + conf.EXCHANGE_RATE_FILE, str(ex))

    return None
