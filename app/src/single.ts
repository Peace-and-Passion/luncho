/**
   Single country.

   @author Hirano Satoshi
 */
import { autoinject } from 'aurelia-framework';
import { App, getFlagEmoji, formatCurrency } from './app';
import { Luncho, LunchoData  } from 'luncho-typescript-fetch';

@autoinject
export class Single {
    app: App;                      // the App
    luncho: Luncho;                // the Luncho object
    lunchoData: LunchoData;        // Luncho data got by the Luncho object

    countryCode: string = 'JP';    // country code
    lunchoValue: number = 100;     // luncho value
    local_currency_string: string; // local currency string
    local_currency_value: number;  // local currency value
    decimals: number;              // decimals of the local currency
    dollar_value: number;          // USD value

    constructor(app: App) {
        this.app = app;
        this.luncho = app.luncho;
    }

    async activate() {
        // download country codes and names
        if (window.origin.indexOf('localhost') >= 0)
            this.countryCode = 'JP';
        else
            this.countryCode = await this.luncho.get_country_code();
        await this.luncho.get_countries(true);
    }

    attached() {
        this.convertFromLuncho();
    }

    // convert from Luncho to local currency and USD
    async convertFromLuncho() {
        this.lunchoData = await this.luncho.get_luncho_data({countryCode: this.countryCode});
        this.decimals = this.app.currencies[this.lunchoData.currency_code].decimals;

        const value = await this.luncho.get_currency_from_luncho(this.lunchoValue, this.countryCode);
        this.local_currency_string = formatCurrency(value, this.decimals);
        this.dollar_value = await this.luncho.get_US_dollar_from_luncho(this.lunchoValue, this.countryCode);
    }

    // convert from local currency to Luncho and USD
    async convertFromLocalCurrency() {
        this.lunchoData = await this.luncho.get_luncho_data({countryCode: this.countryCode});
        this.decimals = this.app.currencies[this.lunchoData.currency_code].decimals;

        const value = Number(this.local_currency_string);
        console.log(value);
        this.lunchoValue = await this.luncho.get_luncho_from_currency(value, this.countryCode);

        this.dollar_value = await this.luncho.get_US_dollar_from_luncho(this.lunchoValue, this.countryCode);
    }
}
