import scrapy

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://www.geeksforgeeks.org/fundamentals-of-algorithms/?ref=shm_outind']

    def parse(self, response):
        # Extract links from the current page
        links = response.css('a::attr(href)').extract()

        # Save HTML content to a file
        filename = response.url.replace('://', '_').replace('/', '_') + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        self.log(f'Saved file {filename}')

        # Follow links to the next page
        for link in links:
            yield response.follow(link, callback=self.parse)
