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
from typing import cast, Any, TypedDict
import pycountry
import pycountry_convert

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


def init(use_dummy_data: bool) -> None:  #pylint: disable=too-many-statements,unused-argument
    ''' Initialize this module.

       Args:
          use_dummy_data  True to use dummy data file.
    '''

    from src import exchange_rate  #pylint: disable=import-outside-toplevel
    global Country_Metadata, Countries, CountryCode_Names #pylint: disable=invalid-name,global-variable-not-assigned

    if not os.getcwd().endswith('server') and not conf.IS_APPENGINE:
        os.chdir("server")

    def process_one_country(data: Any) -> None:
        ''' Process a country metadata and put it in Country_Metadata map.

         ICP_FILE contains for countries and regions as following.

          ITA,Italian Republic,EUR: Euro,Italy,Capital-city only
          JAM,Jamaica,JMD: Jamaican Dollar,Jamaica,...
          JPN,Japan,JPY: Yen,Japan,Capital-city only

        '''

        country_data: Any

        country_code3 = data['Code']     # ISO 3 letter code
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

            data['table_name'] = data['Table Name']
            del data['Table Name']
            # coverage
            coverage: str | None = data.get('Household consumption price survey: Geographical coverage')
            del data['Household consumption price survey: Geographical coverage']
            if coverage:
                data['coverage'] = coverage

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

    with open('data/imf-dm-mapping.json', encoding='utf-8') as mapping_file:
        mapping = json.load(mapping_file)

    # build Countries map from Implied PPP conversion rates (National currency per international dollar)
    #
    # PPP_FILE
    #
    # Antigua and Barbuda,1.296,1.283,1.344,(snip),2.046,2.047,2.05
    # Argentina,0,0,0,0,0,0,0,0,0.001,0.016,(snip), 41.198,56.231,70.931,84.788,97.39,108.15
    #
    with open(PPP_FILE, newline='', encoding="utf_8_sig") as imf_file:
        imf_reader  = csv.DictReader(imf_file)

        # 193 countries and regions in the file
        for data in imf_reader:
            title = 'Implied PPP conversion rate (National currency per international dollar)'
            table_name: str | None = data.get(title)
            if not table_name or not data.get('2020'):
                continue
            table_name = mapping.get(table_name, table_name)
            #pdb.set_trace()
            country_code: str | None = None
            for code, metadata in Country_Metadata.items(): #type: str, CountryMetadataType
                # print('code=' + code)
                # print('metadata = ' + str(metadata))
                if metadata['table_name'] == table_name:
                    country_code = code
            assert country_code, 'country code for ' + cast(str, table_name)
            ppps = {}
            for year in range(1980, 2100):
                ppp = data.get(str(year))
                if ppp is None or ppp == 'no data':
                    continue
                ppps[year] = float(ppp)

            if country_code in ('TL', 'KP'): # Timor-Leste and North Korea are in asia.
                continent_code = 'AS'
            else:
                continent_code = pycountry_convert.country_alpha2_to_continent_code(country_code)
            # print(str(ppps))

            # because ppp and dollar_per_luncho varies depending time, we fill them when API is called.

            # Countries[country_code] = {
            #     'year_ppp': ppps,
            #     'country_code': country_code,
            #     'currency_code': Country_Metadata[country_code]['currency_code'],
            #     'continent_code': continent_code,
            #     'currency_name': Country_Metadata[country_code]['currency_name'],
            #     'country_name': Country_Metadata[country_code]['name']
            # }
            Countries[country_code] = Country(
                year_ppp = ppps,
                country_code = country_code,
                currency_code = Country_Metadata[country_code]['currency_code'],
                continent_code = continent_code,
                currency_name = Country_Metadata[country_code]['currency_name'],
                country_name = Country_Metadata[country_code]['name'],
            )
            CountryCode_Names[country_code] = Country_Metadata[country_code]['name']

        # Countries['KP'] = Countries.get('KP') or {
        #     'year_ppp': {},
        #     'country_code': 'KP',
        #     'currency_code': 'KPW',
        #     'continent_code': 'AS',
        #     'currency_name': "North Korean Won",
        #     'country_name': "Korea, Democratic People's Republic of"
        # }

        #print(str(Countries))
        #print(CountryCode_Names)

def update() -> None:
    ''' Update Countries to reflect the latest exchange rates. '''

    from src import exchange_rate  #pylint: disable=import-outside-toplevel
    year: int = datetime.datetime.today().year
    logging.info('ppp_data.update()')

    with exchange_rate.global_variable_lock:
        for _country_code, country in Countries.items():  #type: CountryCode, Country
            country.ppp = country.year_ppp.get(year, 0.0) if country.year_ppp else None # country's ppp of this year
            country.exchange_rate = exchange_rate.exchange_rate_per_USD(country.currency_code)
            country.dollar_per_luncho = SDR_PER_LUNCHO / exchange_rate.SDR_Per_Dollar
            country.expiration = exchange_rate.expiration
            # country['ppp'] = country['year_ppp'].get(year, 0.0)  # country's ppp of this year
            # country['exchange_rate'] = exchange_rate.exchange_rate_per_USD(country['currency_code'])
            # country['dollar_per_luncho'] = SDR_PER_LUNCHO / exchange_rate.SDR_Per_Dollar
            # country['expiration'] = exchange_rate.expiration
