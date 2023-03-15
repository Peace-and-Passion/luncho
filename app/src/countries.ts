import { autoinject, TaskQueue, observable } from 'aurelia-framework';
import { App, getFlagEmoji } from './app';
import { Luncho, LunchoData } from 'luncho-typescript-fetch';
import { Chart, ChartConfiguration, ChartItem } from 'chart.js/auto';

@autoinject
export class Countries {
    app: App;
    luncho: Luncho
    taskQueue: TaskQueue;
    lunchoValue: number = 100;
    lunchoDatas: LunchoData[];      // this is the table data.
    maxCountryInDollar: number;
    graphElem: ChartItem;
    graph: any;
    @observable $displayData: LunchoData[];
    $displayDataChanged() {
        // sort changed. redraw graph
        if (this.graph) {
            this.graph.destroy();
            this.drawGraph();
        }
    }

    showCode = false;

    filters = [
        {value: '', keys: ['country_name', 'currency_name']},
        {value: '', keys: ['continent_code']},
    ];

    constructor(app: App, taskQueue: TaskQueue) {
        this.app = app;
        this.taskQueue = taskQueue;
        this.luncho = app.luncho;
    }

    attached() {
        this.lunchosForCountries()
            .then(() => this.drawGraph());
    }

    async lunchosForCountries(): Promise<void> {
        await this.luncho.get_all_luncho_data();
        this.maxCountryInDollar = 0;

        // remove Zinbabe
        delete this.luncho.lunchoDataCache['ZW'];

        for (var countryCode of Object.keys(this.luncho.lunchoDataCache)) {

            // destructive, but don't care
            this.luncho.lunchoDataCache[countryCode]['local_currency_value'] = await this.luncho.get_currency_from_luncho(this.lunchoValue, countryCode);
            this.luncho.lunchoDataCache[countryCode]['dollar_value'] = await this.luncho.get_US_dollar_from_luncho(this.lunchoValue, countryCode);
            if (this.luncho.lunchoDataCache[countryCode]['dollar_value'] > this.maxCountryInDollar)
                this.maxCountryInDollar = this.luncho.lunchoDataCache[countryCode]['dollar_value'];
            this.luncho.lunchoDataCache[countryCode]['emoji'] = getFlagEmoji(countryCode);
        }

        this.lunchoDatas = [];
        for (var countryCode of Object.keys(this.luncho.lunchoDataCache)) {
            this.lunchoDatas.push(this.luncho.lunchoDataCache[countryCode]);
        }
    }

    drawGraph() {
        Chart.defaults.font.size = 10;
        Chart.defaults.font.lineHeight = 1.0;
        const opts: ChartConfiguration = {
            type: 'bar',
            data: {
                labels: this.$displayData.map((lunchoData: LunchoData) => {
                    return lunchoData['emoji'] + ' ' + lunchoData.country_name
                }),
                datasets: [
                    {
                        label: 'Luncho in $USD',
                        data: this.$displayData.map((lunchoData: LunchoData) => lunchoData['dollar_value']),
                        borderColor: '#406090',
                        backgroundColor: '#406090',

                        // stand out the current country. not work yet, but isn't this good?
                        // backgroundColor: <any>this.$displayData.map((lunchoData: LunchoData) => {
                        //     return (lunchoData['country_code'] === this.app.countryCode) ? '#906040' : '#406090';
                        // }),
                    }
                ]
            },
            options: {
                plugins: {
                    legend: {
                        labels: {
                            font: {
                                size: 15    // legent font size
                            }
                        }
                    }
                }
            }
        };

        this.graph = new Chart(<HTMLCanvasElement>document.getElementById('graph'), opts);
    }
}
