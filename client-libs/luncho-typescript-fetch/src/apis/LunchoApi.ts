/* tslint:disable */
/* eslint-disable */
/**
 * Custom title
 * This is a very custom OpenAPI schema
 *
 * The version of the OpenAPI document: 2.5.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


import * as runtime from '../runtime';
import {
    HTTPValidationError,
    HTTPValidationErrorFromJSON,
    HTTPValidationErrorToJSON,
    IMFPPPCountry,
    IMFPPPCountryFromJSON,
    IMFPPPCountryToJSON,
    LunchoResult,
    LunchoResultFromJSON,
    LunchoResultToJSON,
} from '../models';

export interface LunchoRequest {
    countryCode?: string;
    lunchoValue?: number;
}

export interface LunchosRequest {
    lunchoValue: number;
}

/**
 * 
 */
export class LunchoApi extends runtime.BaseAPI {

    /**
     * Returns country data for all countries.
     * Countries
     */
    async countriesRaw(): Promise<runtime.ApiResponse<{ [key: string]: IMFPPPCountry; }>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/countries`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => runtime.mapValues(jsonValue, IMFPPPCountryFromJSON));
    }

    /**
     * Returns country data for all countries.
     * Countries
     */
    async countries(): Promise<{ [key: string]: IMFPPPCountry; }> {
        const response = await this.countriesRaw();
        return await response.value();
    }

    /**
     * Luncho
     */
    async lunchoRaw(requestParameters: LunchoRequest): Promise<runtime.ApiResponse<LunchoResult>> {
        const queryParameters: any = {};

        if (requestParameters.countryCode !== undefined) {
            queryParameters['country_code'] = requestParameters.countryCode;
        }

        if (requestParameters.lunchoValue !== undefined) {
            queryParameters['luncho_value'] = requestParameters.lunchoValue;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/luncho`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => LunchoResultFromJSON(jsonValue));
    }

    /**
     * Luncho
     */
    async luncho(requestParameters: LunchoRequest): Promise<LunchoResult> {
        const response = await this.lunchoRaw(requestParameters);
        return await response.value();
    }

    /**
     * Lunchos
     */
    async lunchosRaw(requestParameters: LunchosRequest): Promise<runtime.ApiResponse<Array<LunchoResult>>> {
        if (requestParameters.lunchoValue === null || requestParameters.lunchoValue === undefined) {
            throw new runtime.RequiredError('lunchoValue','Required parameter requestParameters.lunchoValue was null or undefined when calling lunchos.');
        }

        const queryParameters: any = {};

        if (requestParameters.lunchoValue !== undefined) {
            queryParameters['luncho_value'] = requestParameters.lunchoValue;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/lunchos`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => jsonValue.map(LunchoResultFromJSON));
    }

    /**
     * Lunchos
     */
    async lunchos(requestParameters: LunchosRequest): Promise<Array<LunchoResult>> {
        const response = await this.lunchosRaw(requestParameters);
        return await response.value();
    }

}