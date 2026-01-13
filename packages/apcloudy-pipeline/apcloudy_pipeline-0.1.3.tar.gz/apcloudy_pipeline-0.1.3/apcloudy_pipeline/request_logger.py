import time

from scrapy import signals

from apcloudy_pipeline.collector import DataCollector
from apcloudy_pipeline.utils import request_fingerprint


class APCloudyRequestLogger:
    """
    Scrapy extension to log successful requests.
    Failed requests are handled by APCloudyErrorMiddleware.
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()

        # Use shared collector
        if not hasattr(crawler, 'apcloudy_collector'):
            crawler.apcloudy_collector = DataCollector()
        ext.collector = crawler.apcloudy_collector

        crawler.signals.connect(ext.request_scheduled, signal=signals.request_scheduled)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        return ext

    def request_scheduled(self, request, spider):
        """Store start time for response time calculation"""
        request.meta['start_time'] = time.time()

    def response_received(self, response, request, spider):
        """Log successful responses (including non-200 status codes)"""
        start_time = request.meta.get('start_time', time.time())
        response_time = time.time() - start_time

        request_log = {
            "url": request.url,
            "method": request.method,
            "status_code": response.status,
            "response_time": round(response_time, 2),
            "fingerprint": request_fingerprint(request),
            "error": None,
            "success": 200 <= response.status < 300
        }

        self.collector.add_request(request_log)
