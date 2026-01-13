import re
import time

from .utils import request_fingerprint


class APCloudyErrorMiddleware:
    """
    Downloader middleware to catch and log all request errors/exceptions.
    Works in tandem with APCloudyRequestLogger (which handles successful responses).
    """

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()

        # Use shared collector
        if not hasattr(crawler, 'apcloudy_collector'):
            from .collector import DataCollector
            crawler.apcloudy_collector = DataCollector()
        middleware.collector = crawler.apcloudy_collector

        return middleware

    def process_exception(self, request, exception, spider):
        """Log failed requests with error details"""
        start_time = request.meta.get('start_time', time.time())
        response_time = time.time() - start_time

        # Extract status code from exception
        status_code = self._extract_status_code(exception)

        request_log = {
            "url": request.url,
            "method": request.method,
            "status_code": status_code,
            "response_time": round(response_time, 2),
            "fingerprint": request_fingerprint(request),
            "error": f"{exception.__class__.__name__}: {str(exception)}",
            "success": False
        }

        self.collector.add_request(request_log)

        # Return None to let Scrapy handle the exception normally
        return None

    def _extract_status_code(self, exception):
        """Extract HTTP status code from exception"""
        # Check if exception message contains status code like [400], [404]
        status_match = re.search(r'\[(\d{3})]', str(exception))
        if status_match:
            return int(status_match.group(1))

        # Check if exception has status attribute
        if hasattr(exception, 'status'):
            return exception.status

        # Check if exception has response with status
        if hasattr(exception, 'response') and hasattr(exception.response, 'status'):
            return exception.response.status

        return 0
