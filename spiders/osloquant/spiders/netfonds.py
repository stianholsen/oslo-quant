# -*- coding: utf-8 -*-
import scrapy
import datetime

class NetfondsSpider(scrapy.Spider):
    name = 'netfonds'
    allowed_domains = ['netfonds.no']
    start_urls = ['http://www.netfonds.no/quotes/exchange.php']

    def parse(self, response):

        # select the table which contains the ticker list
        table_rows = response.css(".hcontent > .com tr")

        for row in table_rows:

            # if this row contains the table header
            if(len(row.css("th"))):

                # sanity check: check that the columns are as expected
                columns = row.css("th::text").extract()
                assert columns == ['Tick', 'Åpning', 'Høy', 'Lav', 'Siste', 'Volum', 'Verdi']

            # if this row contains table data
            elif(len(row.css("td"))):

                # extract ticker name and url from this table row
                ticker = row.css("a::text").extract_first()
                url = row.css("a::attr(href)").extract_first()

                # convert the relative URL to absolute
                absolute_url = response.urljoin(url)

                # proceed to scrape the instrument page
                yield scrapy.Request(url=absolute_url, callback=self.parse_instrument)

            else:
                self.logger.error("This table row contains neither td or th elements")

    def parse_instrument(self, response):

        # Extract the ticker and market name from the end of the request URL.
        # Typically: ttp://www.netfonds.no/quotes/ppaper.php?paper=AFG.OSE
        ticker = response.url.split("?paper=")[-1]

        # the instrument full name is at the top of the menu table to the left
        long_name = response.css(".hsidetable .helemselected a::text").extract_first()

        # construct the download url for the semicolon separated CSV containing market data
        url = "http://hopey.netfonds.no/paperhistory.php?paper=" + ticker + "&csv_format=sdv"

        yield scrapy.Request(url=url,
                             callback=self.parse_sdv,
                             meta={'ticker': ticker, 'name': long_name})

    def parse_sdv(self, response):

        # unpack the meta-values passed from the previous request
        ticker = response.meta['ticker']
        name = response.meta['name']

        # Split
        lines = response.text.strip().split("\n")


        # remove the first item, which is the column headers
        header = lines.pop(0)

        # sanity check: check that the header row is as expected
        assert header == 'quote_date;paper;exch;open;high;low;close;volume;value'

        # the parsed data
        data = {}

        # fill in the data
        for line_num, line in enumerate(lines):

            # unpack row items)
            (date, paper, exchange, open_price, high_price,
             low_price, close_price, volume, value) = line.split(";")

            # parse row items
            date = datetime.datetime.strptime(date, '%Y%m%d').timestamp()
            open_price = float(open_price)
            high_price = float(high_price)
            low_price = float(low_price)
            close_price = float(close_price)
            volume = float(volume)
            value = float(value)

            # data row indexed by date
            data[date] = {'open_price': open_price,
                          'high_price': high_price,
                          'low_price': low_price,
                          'close_price': close_price,
                          'volume': volume,
                          'value': value}

        # print some info so that the user can see what's going on
        self.logger.info("Scraped " + ticker)

        # returned the parsed data in this storage class
        return {'ticker': ticker,
                'name': name,
                'data': data}