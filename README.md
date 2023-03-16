# Luncho de Peace

A library for currency conversion among local currency, US Dollar, and Luncho that is a
common value index, taking the price level of each country into account using Purchase Power Parity
(PPP).  Also with an API server and an app.

- [Demo on the official Luncho de Peace web site](https://luncho-de-peace.org)
- [Free Luncho API server](https://luncho-de-peace.org/v1/luncho-data?country_code=JP)
- [About Luncho, how it works](https://luncho-de-peace.org/about)

### Examples

To get the local currency value of a country from a US dollar value in US, taking the
   price level of the country into account by factor 0 to 1.0.

   ```
      const jpy = await this.luncho.get_currency_from_US_dollar(50.0, 'JP', 1.0)
   ```

To get the local currency value of a country from a Luncho value, taking the
   price level of the country into account by factor 0 to 1.0.

   ```
      const local_currency_value = await this.luncho.get_currency_from_luncho(100.0, 'JP', 1.0);
   ```

 To get the Luncho value of a country from a local currency value.

   ```
      const luncho_value = await this.luncho.get_luncho_from_currency(50.0, 'JP', 1.0);
   ```

To get the US Dollar value of a country from a Luncho value, taking the
     price level of the country into account by factor 0 to 1.0.

   ```
      const dollar_value = await this.luncho.get_US_dollar_from_luncho(100, 'JP', 1.0);
   ```

To estimate country code from IP address

   ```
      this.countryCode = await this.luncho.get_country_code();
   ```


### Common value index that you can have simple lunch in every country with 100 Luncho.

Useful for currency conversion on pricing pages and wages for mitigating the inequality problem among countries. It's based on purchase power parity (PPP) and World comparison Program (ICP).

###

A luncho value shows the same value in any country taking its price levels into account. For example, with
      100 Luncho, you can have simple lunch in India, in Brazil, in USA, in Japan, and in any other
      countries.

In India 100 Luncho is equivalent to 160 rupee ($2.19 US dollar), while the same 100 Luncho
      is equivalent to 17 real ($3.12 US dollar) in Brazil. In USA, 100 Luncho is about $7.21 US
        dollar. All are the same value because everything is just 100 Luncho.

## Usages

- [README for Python client library](./luncho-python/README.markdown)
- [README for TypeScript and Fetch client library](./luncho-typescript-fetch/README.markdown)

- [README for the Luncho server](./server/README.org)
- [README for the Luncho app](./app/README.org)

Send PRs if you make client libs for other languages.

### API change

- Added get_luncho_from_currency() and get_currency_from_US_dollar().
- 100 Luncho is 6 SDR since 16th March, 2023.

## Bonus

*Grow your product with Luncho.*

Once you use Luncho in your pricing page, people in developing countries who are not able to
buy your digital service will become to afford to buy it. Luncho will accelerate growth of
your user base and your revenue beyond the current ones without Luncho.

## Note

Luncho de Peace is a derived work of AIST Luncho.
