import { autoinject } from 'aurelia-framework';
import {RouteConfig, NavigationInstruction} from 'aurelia-router';
import { App } from './app';
import { Luncho, LunchoData  } from 'luncho-typescript-fetch';

@autoinject
export class About {
    app: App;                      // the App
    luncho: Luncho;                // the Luncho object
    expiration: string;

    saleForce_luncho: number;
    saleForce_lunch: number;
    saleForce_USD: number;
    wage_luncho: number;
    lunchoData_US: LunchoData;

    constructor(app: App) {
        this.app = app;
        this.luncho = app.luncho;
    }

    async activate(_params: any, _routeConfig: RouteConfig, _navigationInstruction: NavigationInstruction): Promise<void> {
        await this.luncho.get_all_luncho_data();
        const lunchoData_US: LunchoData = await this.luncho.get_luncho_data({countryCode: 'US'});
        this.expiration = new Date(lunchoData_US.expiration * 1000).toLocaleDateString();

        this.saleForce_USD = 75;
        this.saleForce_luncho = await this.luncho.get_luncho_from_currency(75, 'US');
        this.saleForce_lunch = Math.round(this.saleForce_luncho/100 * 10) / 10;

        this.wage_luncho = 50000;
    }
}
