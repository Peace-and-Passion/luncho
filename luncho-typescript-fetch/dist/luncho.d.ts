/**
  Fast Luncho API with caching. Use this and don't this LunchoApi.ts.

  @author: HIRANO Satoshi
  @date: 2021-5-15
*/
import { LunchoData } from './models';
import { LunchoApi, LunchoDataRequest } from './apis/LunchoApi';
import { Configuration } from './runtime';
export declare type CountryCode = string;
/**
    Fast Luncho API client by caching.
        This class converts values between Luncho and a specified currency using cached
        LunchoData. If the cache is not available, it delegates to LunchoApi which
        is a auto-generated class.

        In the cases of error, methods throws an Error. See LunchoApi.ts for error.
 */
export declare class Luncho extends LunchoApi {
    lunchoDataCache: {
        [key: string]: LunchoData;
    };
    allLunchoDatasExpiration: number;
    countryCache: {
        [key: string]: string;
    };
    countryCodeCache: string;
    IntlCountryNames: any;
    IntlCurrencyNames: any;
    /**
       Initialize Luncho object with the given Configuration.

       For Configuration, see runtime.Configuration.
      */
    constructor(configuration: Configuration);
    /**
        Returns the local currency value of the country from the US dollar value in US, taking the
        price level of the country into account by factor 0 to 1.0.

          @param lunchoValue A Luncho value to be converted.
          @param countryCode A 2-letter country code. The result is in the primary currency of the country.
          @param factor      A number how much the price level considered (reflected).
                             0 for no consideration and 1.0 for full consideration.
          @return A value in local currency for the lunchoValue.
    */
    get_currency_from_US_dollar(usdValue: number, countryCode: string, factor?: number): Promise<number>;
    /**
        Returns the local currency value of the country from the Luncho value, taking the
        price level of the country into account by factor 0 to 1.0.

       @param lunchoValue A Luncho value to be converted.
       @param countryCode A 2-letter country code. The result is in the primary currency of the country.
       @param factor      A number how much the price level considered (reflected).
                          0 for no consideration and 1.0 for full consideration.
       @return Promise for a value in local currency for the lunchoValue.
    */
    get_currency_from_luncho(lunchoValue: number, countryCode: string, factor?: number): Promise<number>;
    /**
       Returns the Luncho value of the country from the local currency value.

       @param localValue A value in local currency to be converted.
       @param countryCode A 2-letter country code of the country for the localValue.
       @return Promise for a value in Luncho for the localValue.
    */
    get_luncho_from_currency(localValue: number, countryCode: string): Promise<number>;
    /**
       Returns the US Dollar value of the country from the Luncho value, taking the
        price level of the country into account by factor 0 to 1.0.

       @param lunchoValue A Luncho value to be converted.
       @param countryCode A 2-letter country code.
       @param factor      A number how much the price level considered (reflected).
                          0 for no consideration and 1.0 for full consideration.
       @return Promise for a value in US dollar for the lunchoValue.
    */
    get_US_dollar_from_luncho(lunchoValue: number, countryCode: string, factor?: number): Promise<number>;
    /**
       Returns a Luncho data for the given country code.

       @param param A LunchoDataRequest object.
       @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
       @return Promise for LunchoData for param.country_code.
    */
    get_luncho_data(param: LunchoDataRequest, localName?: boolean): Promise<LunchoData>;
    /**
       Load and get a dict of LunchoData of all supported countries.  Data size is about 40KB.

       If you use data of all countries, call this before in order to load all LunchoDatas at once.

       @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
       @return Promise for a dict of Luncho data of all countries.
    */
    get_all_luncho_data(localName?: boolean): Promise<{
        [key: string]: LunchoData;
    }>;
    /**
       Returns a dict of supported country codes and country names.

       @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
       @return Promise for a dict of supported country codes and country names.
    */
    get_countries(localName?: boolean): Promise<{
        [key: string]: string;
    }>;
    /**
       Returns an estimated country code with IP address. Available only if the server supports.
    */
    get_country_code(): Promise<string>;
}
