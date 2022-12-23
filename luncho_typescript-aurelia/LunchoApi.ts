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

import { autoinject } from 'aurelia-framework';
import { HttpClient } from 'aurelia-http-client';
import { Api } from './Api';
import { AuthStorage } from './AuthStorage';
import {
  LunchoData,
} from './models';

/**
 * allLunchoData - parameters interface
 */
export interface IAllLunchoDataParams {
}

/**
 * countries - parameters interface
 */
export interface ICountriesParams {
}

/**
 * countryCode - parameters interface
 */
export interface ICountryCodeParams {
}

/**
 * health - parameters interface
 */
export interface IHealthParams {
}

/**
 * lunchoData - parameters interface
 */
export interface ILunchoDataParams {
  countryCode: string;
}

/**
 * LunchoApi - API class
 */
@autoinject()
export class LunchoApi extends Api {

  /**
   * Creates a new LunchoApi class.
   *
   * @param httpClient The Aurelia HTTP client to be injected.
   * @param authStorage A storage for authentication data.
   */
  constructor(httpClient: HttpClient, authStorage: AuthStorage) {
    super(httpClient, authStorage);
  }

  /**
   * All Luncho Data
   * Returns A dict of LunchoDatas for supported countries. Data size is about 40KB. - **return**: Dict[CountryCode, LunchoData] A dict of a country code and LunchoData.
   */
  async allLunchoData(): Promise<{ [key: string]: LunchoData; }> {
    // Verify required parameters are set

    // Create URL to call
    const url = `${this.basePath}/v1/all-luncho-data`;

    const response = await this.httpClient.createRequest(url)
      // Set HTTP method
      .asGet()

      // Send the request
      .send();

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw new Error(response.content);
    }

    // Extract the content
    return response.content;
  }

  /**
   * Countries
   * Returns a dict of supported country codes and names so that you can show a dropdown list of countries. Data size is about 3.5KB.    E.g. {\&#39;JP\&#39;: \&#39;Japan\&#39;, \&#39;US\&#39;: \&#39;United States\&#39;...}.     If data for a country is not available, either its ppp or exchange_rate is 0.    - **return**: Dict[CountryCode, str] A dict of a country code and country name.
   */
  async countries(): Promise<{ [key: string]: string; }> {
    // Verify required parameters are set

    // Create URL to call
    const url = `${this.basePath}/v1/countries`;

    const response = await this.httpClient.createRequest(url)
      // Set HTTP method
      .asGet()

      // Send the request
      .send();

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw new Error(response.content);
    }

    // Extract the content
    return response.content;
  }

  /**
   * Country Code
   * Returns country code. This is available only when the server runs on Google App Engine. - **X_Appengine_Country**: Internal use. Ignore this. - **return**: str. A country code.
   */
  async countryCode(): Promise<string> {
    // Verify required parameters are set

    // Create URL to call
    const url = `${this.basePath}/v1/country-code`;

    const response = await this.httpClient.createRequest(url)
      // Set HTTP method
      .asGet()

      // Send the request
      .send();

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw new Error(response.content);
    }

    // Extract the content
    return response.content;
  }

  /**
   * Health
   * Do nothing other than telling it\&#39;s OK.
   */
  async health(): Promise<any> {
    // Verify required parameters are set

    // Create URL to call
    const url = `${this.basePath}/v1/health`;

    const response = await this.httpClient.createRequest(url)
      // Set HTTP method
      .asGet()

      // Send the request
      .send();

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw new Error(response.content);
    }

    // Extract the content
    return response.content;
  }

  /**
   * Luncho Data
   * Returns LunchoData that is needed to convert between Luncho and local currency of the countryCode.   If data for the country is not available either ppp or exchange_rate is 0. Data size is about 400 bytes.  - **country_code**: client provided country code in ISO-3166-1-2 formant like \&#39;JP\&#39; - **return**: LunchoData
   * @param params.countryCode 
   */
  async lunchoData(params: ILunchoDataParams): Promise<LunchoData> {
    // Verify required parameters are set
    this.ensureParamIsSet('lunchoData', params, 'countryCode');

    // Create URL to call
    const url = `${this.basePath}/v1/luncho-data`;

    const response = await this.httpClient.createRequest(url)
      // Set HTTP method
      .asGet()
      // Set query parameters
      .withParams({ 
        'country_code': params['countryCode'],
      })

      // Send the request
      .send();

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw new Error(response.content);
    }

    // Extract the content
    return response.content;
  }

}

