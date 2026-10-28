"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const LunchoApi_1 = require("./apis/LunchoApi");
const currencyFractionDigits = {};
/**
 * Returns the ISO 4217 minor-unit digits supplied by the JavaScript runtime.
 *
 * @param currencyCode ISO 4217 currency code.
 * @returns Number of fractional digits used for the currency.
 */
function fractionDigitsForCurrency(currencyCode) {
    if (currencyFractionDigits[currencyCode] === undefined) {
        currencyFractionDigits[currencyCode] = new Intl.NumberFormat('en', {
            style: 'currency', currency: currencyCode,
        }).resolvedOptions().maximumFractionDigits;
    }
    return currencyFractionDigits[currencyCode];
}
/**
 * Rounds a value to the ISO 4217 minor-unit digits of a currency.
 *
 * @param value Value to round.
 * @param currencyCode ISO 4217 currency code.
 * @returns Rounded value.
 */
function roundForCurrency(value, currencyCode) {
    const multiplier = Math.pow(10, fractionDigitsForCurrency(currencyCode));
    return Math.round(value * multiplier) / multiplier;
}
/**
    Fast Luncho API client by caching.
        This class converts values between Luncho and a specified currency using cached
        LunchoData. If the cache is not available, it delegates to LunchoApi which
        is a auto-generated class.

        In the cases of error, methods throws an Error. See LunchoApi.ts for error.
 */
class Luncho extends LunchoApi_1.LunchoApi {
    /**
       Initialize Luncho object with the given Configuration.

       For Configuration, see runtime.Configuration.
      */
    constructor(configuration) {
        super(configuration);
        this.lunchoDataCache = {}; // Cache {CountryCode: LunchoData}
        this.allLunchoDatasExpiration = 0;
        // prepare local name converters
        if (Intl.DisplayNames) {
            var supportedLocales = Intl.DisplayNames.supportedLocalesOf(browserLocale());
            if (supportedLocales.length == 0)
                supportedLocales = ['en'];
            this.IntlCountryNames = new Intl.DisplayNames(supportedLocales[0], { type: 'region' });
            this.IntlCurrencyNames = new Intl.DisplayNames(supportedLocales[0], { type: 'currency' });
        }
    }
    /**
        Returns the local currency value of the country from the US dollar value in US, taking the
        price level of the country into account by factor 0 to 1.0.

          @param lunchoValue A Luncho value to be converted.
          @param countryCode A 2-letter country code. The result is in the primary currency of the country.
          @param factor      A number how much the price level considered (reflected).
                             0 for no consideration and 1.0 for full consideration.
          @return A value in local currency for the lunchoValue.
    */
    get_currency_from_US_dollar(usdValue, countryCode, factor = 1.0) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.get_luncho_data({ countryCode: countryCode })
                .then((lunchoData) => {
                const local_currency_value = usdValue * lunchoData.ppp;
                const localCurrencyValueWithFactor = usdValue - (usdValue - local_currency_value) * factor;
                return roundForCurrency(localCurrencyValueWithFactor, lunchoData.currency_code);
            });
        });
    }
    /**
        Returns the local currency value of the country from the Luncho value, taking the
        price level of the country into account by factor 0 to 1.0.

       @param lunchoValue A Luncho value to be converted.
       @param countryCode A 2-letter country code. The result is in the primary currency of the country.
       @param factor      A number how much the price level considered (reflected).
                          0 for no consideration and 1.0 for full consideration.
       @return Promise for a value in local currency for the lunchoValue.
    */
    get_currency_from_luncho(lunchoValue, countryCode, factor = 1.0) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.get_luncho_data({ countryCode: countryCode })
                .then((lunchoData) => {
                const US_value = lunchoData.dollar_per_luncho * lunchoValue;
                const local_currency_value = US_value * lunchoData.ppp;
                const dollar_value = local_currency_value / lunchoData.exchange_rate;
                const dollar_value_with_factor = US_value - (US_value - dollar_value) * factor;
                const localCurrencyValueWithFactor = dollar_value_with_factor * lunchoData.exchange_rate;
                // const US_value = lunchoData.dollar_per_luncho * lunchoValue;
                // const local_currency_value = US_value * lunchoData.ppp;
                // const local_currency_value_with_factor = US_value - (US_value - local_currency_value) * factor;
                return roundForCurrency(localCurrencyValueWithFactor, lunchoData.currency_code);
            });
        });
    }
    /**
       Returns the Luncho value of the country from the local currency value.

       @param localValue A value in local currency to be converted.
       @param countryCode A 2-letter country code of the country for the localValue.
       @return Promise for a value in Luncho for the localValue.
    */
    get_luncho_from_currency(localValue, countryCode) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.get_luncho_data({ countryCode: countryCode })
                .then((lunchoData) => {
                let luncho_value = (localValue / lunchoData.ppp) / lunchoData.dollar_per_luncho;
                // round
                luncho_value = Math.round(luncho_value);
                //const luncho_value = (localValue / lunchoData.ppp) / lunchoData.dollar_per_luncho;
                return luncho_value;
            });
        });
    }
    /**
       Returns the US Dollar value of the country from the Luncho value, taking the
        price level of the country into account by factor 0 to 1.0.

       @param lunchoValue A Luncho value to be converted.
       @param countryCode A 2-letter country code.
       @param factor      A number how much the price level considered (reflected).
                          0 for no consideration and 1.0 for full consideration.
       @return Promise for a value in US dollar for the lunchoValue.
    */
    get_US_dollar_from_luncho(lunchoValue, countryCode, factor = 1.0) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.get_luncho_data({ countryCode: countryCode })
                .then((lunchoData) => {
                if (lunchoData.exchange_rate > 0) {
                    const US_value = lunchoData.dollar_per_luncho * lunchoValue;
                    const local_currency_value = US_value * lunchoData.ppp;
                    const dollar_value = local_currency_value / lunchoData.exchange_rate;
                    let dollar_value_with_factor = US_value - (US_value - dollar_value) * factor;
                    // round
                    dollar_value_with_factor = Math.round(dollar_value_with_factor * 100) / 100;
                    return dollar_value_with_factor;
                }
                else
                    return 0.0;
            });
        });
    }
    /**
       Returns a Luncho data for the given country code.

       @param param A LunchoDataRequest object.
       @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
       @return Promise for LunchoData for param.country_code.
    */
    get_luncho_data(param, localName = true) {
        const _super = name => super[name];
        return __awaiter(this, void 0, void 0, function* () {
            if (param && param.countryCode) {
                const lunchoData = this.lunchoDataCache[param.countryCode];
                // if (lunchoData) {
                if (lunchoData && lunchoData.expiration > Date.now() / 1000) {
                    return Promise.resolve(lunchoData);
                }
            }
            return _super("lunchoData").call(this, param)
                .then((lunchoData) => {
                this.lunchoDataCache[param.countryCode] = lunchoData;
                if (localName && this.IntlCountryNames) {
                    lunchoData['country_name_alpha'] = lunchoData.country_name;
                    lunchoData.country_name = this.IntlCountryNames.of(lunchoData.country_code);
                    lunchoData.currency_name = this.IntlCurrencyNames.of(lunchoData.currency_code);
                }
                return (lunchoData);
            });
        });
    }
    /**
       Load and get a dict of LunchoData of all supported countries.  Data size is about 40KB.

       If you use data of all countries, call this before in order to load all LunchoDatas at once.

       @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
       @return Promise for a dict of Luncho data of all countries.
    */
    get_all_luncho_data(localName = true) {
        const _super = name => super[name];
        return __awaiter(this, void 0, void 0, function* () {
            if (this.allLunchoDatasExpiration > Date.now() / 1000) {
                return Promise.resolve(this.lunchoDataCache);
            }
            return _super("allLunchoData").call(this)
                .then((lunchoDatas) => {
                this.lunchoDataCache = lunchoDatas;
                this.allLunchoDatasExpiration = lunchoDatas['JP'].expiration;
                if (localName && this.IntlCountryNames) {
                    for (var countryCode of Object.keys(this.lunchoDataCache)) {
                        this.lunchoDataCache[countryCode]['country_name_alpha'] = this.lunchoDataCache[countryCode].country_name;
                        this.lunchoDataCache[countryCode].country_name = this.IntlCountryNames.of(countryCode);
                        this.lunchoDataCache[countryCode].currency_name = this.IntlCurrencyNames.of(this.lunchoDataCache[countryCode].currency_code);
                    }
                }
                return (lunchoDatas);
            });
        });
    }
    /**
       Returns a dict of supported country codes and country names.

       @param localName True for country names and currency names in the local lauguage. Ignored if Intl.DisplayNames is not available.
       @return Promise for a dict of supported country codes and country names.
    */
    get_countries(localName = true) {
        const _super = name => super[name];
        return __awaiter(this, void 0, void 0, function* () {
            if (this.countryCache) {
                return Promise.resolve(this.countryCache);
            }
            return _super("countries").call(this)
                .then((countryCache) => {
                this.countryCache = countryCache;
                if (localName && this.IntlCountryNames) {
                    for (var countryCode of Object.keys(this.countryCache)) {
                        this.countryCache[countryCode] = this.IntlCountryNames.of(countryCode);
                    }
                }
                return (countryCache);
            });
        });
    }
    /**
       Returns an estimated country code with IP address. Available only if the server supports.
    */
    get_country_code() {
        const _super = name => super[name];
        return __awaiter(this, void 0, void 0, function* () {
            if (this.countryCodeCache) {
                return Promise.resolve(this.countryCodeCache);
            }
            return _super("countryCode").call(this)
                .then((countryCodeJson) => {
                this.countryCodeCache = JSON.parse(countryCodeJson);
                return (this.countryCodeCache);
            });
        });
    }
}
exports.Luncho = Luncho;
function browserLocale() {
    let lang;
    if (navigator.languages && navigator.languages.length) {
        // latest versions of Chrome and Firefox set this correctly
        lang = navigator.languages[0];
    }
    else if (navigator.userLanguage) {
        // IE only
        lang = navigator.userLanguage;
    }
    else {
        // latest versions of Chrome, Firefox, and Safari set this correctly
        lang = navigator.language || 'en';
    }
    return lang;
}
