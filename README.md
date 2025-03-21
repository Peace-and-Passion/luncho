# Luncho: A universal value index for price comparison across countries, accounting for prices levels and inflation.

Pricing calculator that respects the price levels of countries using Purchase Power Parity (PPP). A library for currency conversion among local currency, US Dollar, and Luncho that is a universal value index. Also with an API server and an app.

- [Demo on the official Luncho web site](https://luncho-index.org)
- [Free Luncho API server](https://luncho-index.org/v1/luncho-data?country_code=JP)
- [About Luncho, how it works](https://luncho-index.org/about)

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


### Currency index for tackling inequality among countries. 100 Luncho gets you a simple lunch anywhere in the world.

Useful for currency conversion on pricing pages and wages for mitigating the inequality problem among countries. It's based on purchase power parity (PPP) and World comparison Program (ICP).

###

A luncho value shows the same value in any country taking its price levels into account. For example, with
      100 Luncho, you can have simple lunch in India, in Brazil, in USA, in Japan, and in any other
      countries.

In India 100 Luncho is equivalent to 191.11 Rupee ($2.31 US dollar), while the same 100 Luncho
      is 20.91 Real ($3.96 US dollar) in Brazil. In USA, 100 Luncho is about $7.97 US
        dollar. All are the same value because everything is just 100 Luncho for a lunch.

## Usages

- [README for Python client library](./luncho-python/README.markdown)
- [README for TypeScript and Fetch client library](./luncho-typescript-fetch/README.markdown)

- [README for the Luncho server](./server/README.org)
- [README for the Luncho app](./app/README.org)


### API change

- Added get_luncho_from_currency() and get_currency_from_US_dollar().
- 100 Luncho is 6 SDR since 16th March, 2023.

## Bonus

*Grow your product with Luncho.*

Once you use Luncho in your pricing page, people in developing countries who are not able to
buy your digital service will become to afford to buy it. Luncho will accelerate growth of
your user base and your revenue beyond the current ones without Luncho.

## Note

Luncho-index is a derived work of AIST Luncho.

## Author

Dr HIRANO Satoshi, Peace and Passion, University of Tokyo

## MIT License

Copyright 2019-2022 The National Institute of Advanced Industrial Science and Technology (AIST), Japan
Copyright 2024 Peace and Passion
