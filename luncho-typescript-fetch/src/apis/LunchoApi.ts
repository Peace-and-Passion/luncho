/* tslint:disable */
/* eslint-disable */
/**
 * Client library for Luncho API. 
 * Use luncho.ts and luncho.py rather than LunchoAPI.ts and others.
 *
 * The version of the OpenAPI document: 0.0.1
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


import * as runtime from '../runtime';
import {
    HTTPValidationError,
    LunchoData,
} from '../models';

export interface LunchoDataRequest {
    countryCode: string;
}

/**
 * 
 */
export class LunchoApi extends runtime.BaseAPI {

    /**
     * Returns A dict of LunchoDatas for supported countries. Data size is about 40KB. - **return**: dict[CountryCode, LunchoData] A dict of a country code and LunchoData.
     * All Luncho Data
     */
    async allLunchoDataRaw(): Promise<runtime.ApiResponse<{ [key: string]: LunchoData; }>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/v1/all-luncho-data`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response);
    }

    /**
     * Returns A dict of LunchoDatas for supported countries. Data size is about 40KB. - **return**: dict[CountryCode, LunchoData] A dict of a country code and LunchoData.
     * All Luncho Data
     */
    async allLunchoData(): Promise<{ [key: string]: LunchoData; }> {
        const response = await this.allLunchoDataRaw();
        return await response.value();
    }

    /**
     * Returns a dict of supported country codes and names so that you can show a dropdown list of countries. Data size is about 3.5KB.    E.g. {\'JP\': \'Japan\', \'US\': \'United States\'...}.     If data for a country is not available, either its ppp or exchange_rate is 0.    - **return**: dict[CountryCode, str] A dict of a country code and country name.
     * Countries
     */
    async countriesRaw(): Promise<runtime.ApiResponse<{ [key: string]: string; }>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/v1/countries`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse<any>(response);
    }

    /**
     * Returns a dict of supported country codes and names so that you can show a dropdown list of countries. Data size is about 3.5KB.    E.g. {\'JP\': \'Japan\', \'US\': \'United States\'...}.     If data for a country is not available, either its ppp or exchange_rate is 0.    - **return**: dict[CountryCode, str] A dict of a country code and country name.
     * Countries
     */
    async countries(): Promise<{ [key: string]: string; }> {
        const response = await this.countriesRaw();
        return await response.value();
    }

    /**
     * Returns country code. This is available only when the server runs on Google App Engine. - **X_Appengine_Country**: Internal use. Ignore this. - **return**: str. A country code.
     * Country Code
     */
    async countryCodeRaw(): Promise<runtime.ApiResponse<string>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/v1/country-code`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Returns country code. This is available only when the server runs on Google App Engine. - **X_Appengine_Country**: Internal use. Ignore this. - **return**: str. A country code.
     * Country Code
     */
    async countryCode(): Promise<string> {
        const response = await this.countryCodeRaw();
        return await response.value();
    }

    /**
     * Do nothing other than telling it\'s OK.
     * Health
     */
    async healthRaw(): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/v1/health`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Do nothing other than telling it\'s OK.
     * Health
     */
    async health(): Promise<any> {
        const response = await this.healthRaw();
        return await response.value();
    }

    /**
     * Returns LunchoData that is needed to convert between Luncho and local currency of the countryCode.   If data for the country is not available either ppp or exchange_rate is 0. Data size is about 400 bytes.  - **country_code**: client provided country code in ISO-3166-1-2 formant like \'JP\' - **return**: LunchoData
     * Luncho Data
     */
    async lunchoDataRaw(requestParameters: LunchoDataRequest): Promise<runtime.ApiResponse<LunchoData>> {
        if (requestParameters.countryCode === null || requestParameters.countryCode === undefined) {
            throw new runtime.RequiredError('countryCode','Required parameter requestParameters.countryCode was null or undefined when calling lunchoData.');
        }

        const queryParameters: any = {};

        if (requestParameters.countryCode !== undefined) {
            queryParameters['country_code'] = requestParameters.countryCode;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/v1/luncho-data`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response);
    }

    /**
     * Returns LunchoData that is needed to convert between Luncho and local currency of the countryCode.   If data for the country is not available either ppp or exchange_rate is 0. Data size is about 400 bytes.  - **country_code**: client provided country code in ISO-3166-1-2 formant like \'JP\' - **return**: LunchoData
     * Luncho Data
     */
    async lunchoData(requestParameters: LunchoDataRequest): Promise<LunchoData> {
        const response = await this.lunchoDataRaw(requestParameters);
        return await response.value();
    }

}
