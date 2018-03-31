# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError


class UseErrbackSpider(scrapy.Spider):
    """
    how to use errback
    referenced url:
    https://doc.scrapy.org/en/latest/topics/request-response.html#topics-request-response-ref-errbacks
    """
    name = 'use_errback'
    allowed_domains = ['www.httpbin.org']
    start_urls = [
        "http://www.httpbin.org/",              # HTTP 200 expected
        "http://www.httpbin.org/status/404",    # Not found error
        "http://www.httpbin.org/status/500",    # server issue
        "http://www.httpbin.org:12345/",        # non-responding host, timeout expected
        "http://www.httphttpbinbin.org/",       # DNS error expected
    ]

    def start_requests(self):
        for u in self.start_urls:
            yield Request(u, callback=self.parse_httpbin, errback=self.deal_error, dont_filter=True)

    def parse_httpbin(self, response):
        self.logger.info('Got Successful response from {}'.format(response.url))

    def deal_error(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
