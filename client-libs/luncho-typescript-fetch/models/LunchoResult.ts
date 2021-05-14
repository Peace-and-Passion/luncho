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

import { exists, mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface LunchoResult
 */
export interface LunchoResult {
    /**
     * 
     * @type {number}
     * @memberof LunchoResult
     */
    dollar_value: number;
    /**
     * 
     * @type {number}
     * @memberof LunchoResult
     */
    local_currency_value: number;
    /**
     * 
     * @type {string}
     * @memberof LunchoResult
     */
    currency_code: string;
    /**
     * 
     * @type {string}
     * @memberof LunchoResult
     */
    country_code: string;
    /**
     * 
     * @type {string}
     * @memberof LunchoResult
     */
    country_name: string;
    /**
     * 
     * @type {string}
     * @memberof LunchoResult
     */
    currency_name: string;
    /**
     * 
     * @type {number}
     * @memberof LunchoResult
     */
    ppp?: number;
    /**
     * 
     * @type {number}
     * @memberof LunchoResult
     */
    dollar_per_luncho: number;
    /**
     * 
     * @type {number}
     * @memberof LunchoResult
     */
    exchange_rate?: number;
}

export function LunchoResultFromJSON(json: any): LunchoResult {
    return LunchoResultFromJSONTyped(json, false);
}

export function LunchoResultFromJSONTyped(json: any, ignoreDiscriminator: boolean): LunchoResult {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'dollar_value': json['dollar_value'],
        'local_currency_value': json['local_currency_value'],
        'currency_code': json['currency_code'],
        'country_code': json['country_code'],
        'country_name': json['country_name'],
        'currency_name': json['currency_name'],
        'ppp': !exists(json, 'ppp') ? undefined : json['ppp'],
        'dollar_per_luncho': json['dollar_per_luncho'],
        'exchange_rate': !exists(json, 'exchange_rate') ? undefined : json['exchange_rate'],
    };
}

export function LunchoResultToJSON(value?: LunchoResult | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'dollar_value': value.dollar_value,
        'local_currency_value': value.local_currency_value,
        'currency_code': value.currency_code,
        'country_code': value.country_code,
        'country_name': value.country_name,
        'currency_name': value.currency_name,
        'ppp': value.ppp,
        'dollar_per_luncho': value.dollar_per_luncho,
        'exchange_rate': value.exchange_rate,
    };
}

