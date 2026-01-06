/**
   The Luncho app.

  @author HIRANO Satoshi
  @date  2021/05/12

*/
import { autoinject, TaskQueue } from 'aurelia-framework';
import { Router, RouterConfiguration } from 'aurelia-router'
import { PLATFORM } from 'aurelia-pal';
import { Luncho, Configuration } from 'luncho-typescript-fetch';
import * as browserLocale from 'browser-locale';
import * as countryData from 'country-data-list';
import * as numeral from 'numeral';

@autoinject
export class App {
    public title: string = 'Luncho de Peace: Universal Value Index for the economic inequality problems';
    public router: Router;
    public static app: App;
    show = false;
    public taskQueue: TaskQueue;
    luncho: Luncho;
    countryData = countryData
    countryCode: string;
    continents = {
        'NA': 'North America',
        'SA': 'South America',
        'AS': 'Asia',
        'EU': 'Europe',
        'OC': 'Australia',
        'AF': 'Africa',
    }


    constructor(taskQueue: TaskQueue, router: Router) {
        var basePath: string;
        if (window['origin'].indexOf('localhost') >= 0)
            basePath = 'http://localhost:8000';
        else
            basePath = window['origin'];
        this.luncho = new Luncho(new Configuration({ basePath: basePath }));
        this.luncho.get_country_code()
            .then((code) => this.countryCode = code);

        this.taskQueue = taskQueue;
        this.router = router;
        App.app = this;

        this.patchCountryData();
    }

    /**
       patch country-data-list to refrect recent changes
    */
    patchCountryData() {

        // São Tomé and Príncipe dobra: STD -> STN (2018)
        if (!this.countryData.currencies['STN']) {
            this.countryData.currencies['STN'] = { ... this.countryData.currencies['STD']};
            this.countryData.currencies['STN'].decimals = 2
        }

        // already done in country-data-list
        // // Belarusian ruble: BYR -> BYN (2016)
        // this.countryData.currencies['BYN'] = this.countryData.currencies['BYR']
        // this.countryData.currencies['BYN'].decimals = 2
    }

    toggleSideNav() {
        this.show = !this.show;
    }

    configureRouter(config: RouterConfiguration, router: Router) {
        this.router = router;
        config.title = this.title;
        config.options.pushState = true;
        //config.options.root = '/';

        //config.addPipelineStep('authorize', AuthorizeStep); // add login
        config.map([
            { route: ['', 'countries'], href: '/countries', name: 'countries',
              moduleId: PLATFORM.moduleName('./countries'),
              auth: true, nav: true, title: 'All countries', },
            { route: 'single', href: '/single', name: 'single',
              moduleId: PLATFORM.moduleName('./single'),
              auth: true, nav: true, title: 'One country', },
            { route: 'about', href: 'about', name: 'about',
              moduleId: PLATFORM.moduleName('./about'),
              auth: true, nav: false, title: 'About', },

        ]);

        config.fallbackRoute('/');
    }
}

// get emoji of country flag
export function getFlagEmoji(countryCode: string) {
  const codePoints = countryCode
    .toUpperCase()
    .split('')
      .map((char: string) =>  127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

// format currency
export function formatCurrency(value: number, decimals: number): string {
    var zeros: string = '0.00';

    switch (decimals) {
        case 0: zeros = '0'; break;
        case 1: zeros = '0.0'; break;
        case 2: zeros = '0.00'; break;
        case 3: zeros = '0.000'; break;
    }
    return numeral(value).format(zeros);
}
