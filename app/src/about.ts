import { autoinject } from 'aurelia-framework';
import { App } from './app';
import { Luncho, LunchoData  } from 'luncho-typescript-fetch';

@autoinject
export class About {
    app: App;                      // the App
    luncho: Luncho;                // the Luncho object
    expiration: string;

    constructor(app: App) {
        this.app = app;
        this.luncho = app.luncho;
    }

    async attached() {
        const lunchoData: LunchoData = await this.luncho.get_luncho_data({countryCode: 'US'});
        this.expiration = new Date(lunchoData.expiration * 1000).toLocaleDateString();
    }
}
