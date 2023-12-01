import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import HtmlResponse
import os
import re
import brotli
from multiprocessing import Pool
from urllib.parse import urlparse, quote

class MySpider(CrawlSpider):
    name = 'urbandictionaryspider'
    allowed_domains = ['urbandictionary.com']  # Replace with your domain
    start_urls = ['https://www.urbandictionary.com/']
    visited_urls = set()
    pages_scraped = 0

    custom_settings = {
        'LOG_LEVEL': 'INFO',  # Set the log level to INFO
    }

    rules = (
        Rule(LinkExtractor(allow=('/')), callback='parse_item', follow=True),
    )

    def sanitize_filename(self, url):
        # Parse the URL and use quote to percent-encode each path component
        #parsed_url = urlparse(url)
        sanitized_url = quote(url, safe='')
        return sanitized_url
        
    def compress_content(self, data):
        # Use brotli for compression
        compressed_data = brotli.compress(data)
        return compressed_data

    def compress_and_save(self, args):
        url, body = args
        sanitized_filename = self.sanitize_filename(url)
        compressed_html = self.compress_content(body)
        file_path = f"geeksforgeeks/{sanitized_filename}.brhtml"
        with open(file_path, 'wb') as file:
            file.write(compressed_html)

    def parse_item(self, response: HtmlResponse):
        if response.url in self.visited_urls:
            return

        # Add the URL to the set of visited URLs
        self.visited_urls.add(response.url)

        # Extract the filename from the sanitized URL
        sanitized_filename = self.sanitize_filename(response.url)

        # Compress the HTML content using brotli
        compressed_html = self.compress_content(response.body)

        # Save the compressed HTML content to a file with the sanitized link as the filename
        file_path = f"urbandictionary/{sanitized_filename}.br"
        with open(file_path, 'wb') as file:
            file.write(compressed_html)

        # Increment the count of pages scraped
        self.pages_scraped += 1
        print(f"Pages scraped: {self.pages_scraped}\r", end='', flush=True)

        return

    def parallel_compress(self, responses):
        # Use multiprocessing.Pool for parallel compression
        with Pool() as pool:
            args = [(response.url, response.body) for response in responses]
            pool.map(self.compress_and_save, args)

    def closed(self, reason):
        # Perform parallel compression when the spider is closed
        self.parallel_compress(self.crawler.engine.slot.scheduler.dqs[0]._requests)
        super().closed(reason)
