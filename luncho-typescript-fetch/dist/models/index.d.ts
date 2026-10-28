/**
 *
 * @export
 * @interface HTTPValidationError
 */
export interface HTTPValidationError {
    /**
     *
     * @type {Array<ValidationError>}
     * @memberof HTTPValidationError
     */
    detail?: Array<ValidationError>;
}
/**
 * Data needed to convert between Luncho and local currency.
 * If data for the country is not available, either ppp or exchange_rate is 0.
 * @export
 * @interface LunchoData
 */
export interface LunchoData {
    /**
     *
     * @type {string}
     * @memberof LunchoData
     */
    country_code: string;
    /**
     *
     * @type {string}
     * @memberof LunchoData
     */
    country_name: string;
    /**
     *
     * @type {string}
     * @memberof LunchoData
     */
    continent_code: string;
    /**
     *
     * @type {string}
     * @memberof LunchoData
     */
    currency_code: string;
    /**
     *
     * @type {string}
     * @memberof LunchoData
     */
    currency_name: string;
    /**
     *
     * @type {number}
     * @memberof LunchoData
     */
    exchange_rate?: number;
    /**
     *
     * @type {number}
     * @memberof LunchoData
     */
    ppp?: number;
    /**
     *
     * @type {number}
     * @memberof LunchoData
     */
    dollar_per_luncho?: number;
    /**
     *
     * @type {number}
     * @memberof LunchoData
     */
    expiration?: number;
}
/**
 *
 * @export
 * @interface ValidationError
 */
export interface ValidationError {
    /**
     *
     * @type {Array<string | number>}
     * @memberof ValidationError
     */
    loc: Array<string | number>;
    /**
     *
     * @type {string}
     * @memberof ValidationError
     */
    msg: string;
    /**
     *
     * @type {string}
     * @memberof ValidationError
     */
    type: string;
}
