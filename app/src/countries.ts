/**
   Countries.

   @author Hirano Satoshi
 */
import { autoinject, TaskQueue, observable } from 'aurelia-framework';
import { App, getFlagEmoji, formatCurrency } from './app';
import { Luncho, LunchoData } from 'luncho-typescript-fetch';
import { Chart, ChartConfiguration, ChartItem } from 'chart.js/auto';

@autoinject
export class Countries {
    app: App;                       // the App
    luncho: Luncho;                 // the Luncho library
    taskQueue: TaskQueue;
    showCode = false;               // true to show currency codes
    lunchoValue: number = 100;      // 100 Luncho
    usdString: string;              // $123.45 in USD
    factor: number = 100;           // Factor value in percent. 0 - 100

    lunchoDataOutput: LunchoData[];      // this is the table data.
    @observable $displayData: LunchoData[];   // table data after sorted by aurelia-table
    $displayDataChanged() {
        // sort changed. redraw graph
        if (this.graph) {
            this.drawGraph();
        }
    }
    filters = [                     // sorter filsters for aurelia-table
        {value: '', keys: ['country_name', 'currency_name', 'currency_code', 'country_name_alpha']},
        {value: '', keys: ['continent_code']},
    ];

    graphElem: ChartItem;           // graph HTMLElement
    graph: Chart;                   // graph object


    constructor(app: App, taskQueue: TaskQueue) {
        this.app = app;
        this.taskQueue = taskQueue;
        this.luncho = app.luncho;
    }

    attached() {
        // show the table and the graph
        this.recalcCountriesTableFromLuncho(true)
            .then(() => {
                this.drawGraph();
            });
    }

    // recalculate countries table from this.lunchoValue and factor
    async recalcCountriesTableFromLuncho(updateUSDString: boolean): Promise<void> {
        await this.luncho.get_all_luncho_data();

        if (updateUSDString) {
            const usd: number = await this.luncho.get_US_dollar_from_luncho(this.lunchoValue, 'US');
            this.usdString = formatCurrency(usd, 2);
        }

        // remove Zinbabe
        delete this.luncho.lunchoDataCache['ZW'];

        for (const countryCode of Object.keys(this.luncho.lunchoDataCache)) {

            const lunchoData: any = {};

            try {
                lunchoData.local_currency_value = await this.luncho.get_currency_from_luncho(this.lunchoValue, countryCode, this.factor / 100.0);

                lunchoData.dollar_value = await this.luncho.get_US_dollar_from_luncho(this.lunchoValue, countryCode);

                if (lunchoData.dollar_value) {
                    lunchoData.dollar_value_with_factor = await this.luncho.get_US_dollar_from_luncho(this.lunchoValue, countryCode, this.factor / 100.0);
                }

                lunchoData.emoji = getFlagEmoji(countryCode);

                // Commit only if everything succeeded
                this.luncho.lunchoDataCache[countryCode] = {
                    ...this.luncho.lunchoDataCache[countryCode],
                    ...lunchoData
                };

            } catch (e) {
                console.warn(`Failed to update lunchoData for ${countryCode}`, e);
            }
        }

        this.lunchoDataOutput = [];
        for (var countryCode of Object.keys(this.luncho.lunchoDataCache)) {
            this.lunchoDataOutput.push(this.luncho.lunchoDataCache[countryCode]);
        }
    }

    // recalculate countries table from this.usdstring and factor
    async recalcCountriesTableFromUSD() {
        this.lunchoValue = await this.luncho.get_luncho_from_currency(Number(this.usdString), 'US');
        this.recalcCountriesTableFromLuncho(false);
    }

    // factor value changed
    factorChanged() {
        this.recalcCountriesTableFromLuncho(false)
            .then(() => this.drawGraph());
    }

    // draw the graph
    drawGraph() {
        this.graph?.destroy();
        if (!this.$displayData) return;

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
                        type: 'bar',
                        label: 'Luncho in $USD',
                        data: this.$displayData.map((lunchoData: LunchoData) => lunchoData['dollar_value']),
                        borderColor: '#6080a0',
                        backgroundColor: '#6080a0',

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

        if (this.factor < 100) {
            opts.data.datasets.push({
                type: 'line',
                label: 'With factor',
                data: this.$displayData.map((lunchoData: LunchoData) => lunchoData['dollar_value_with_factor']),
                borderColor: '#a08060',
                backgroundColor: '#a08060',
                pointStyle: false,
            });
        }

        this.graph = new Chart(<HTMLCanvasElement>document.getElementById('graph'), opts);
    }
}
