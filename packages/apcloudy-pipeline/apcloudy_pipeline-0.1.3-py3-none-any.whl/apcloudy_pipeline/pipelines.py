from scrapy import Item, signals

from .client import APCloudyClient
from .collector import DataCollector


class APCloudyItemPipeline:
    """Scrapy item pipeline to collect and send unified data to AP Cloudy backend"""

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)

        # Store collector in crawler for shared access
        if not hasattr(crawler, 'apcloudy_collector'):
            crawler.apcloudy_collector = DataCollector()

        return pipeline

    def __init__(self, crawler):
        self.client = APCloudyClient(crawler)
        self.collector = crawler.apcloudy_collector
        self.batch_size = crawler.settings.getint('APCLOUDY_BATCH_SIZE', 50)

    def process_item(self, item: Item, spider):
        self.collector.add_item(dict(item))

        # Send immediately if total collected data reaches threshold
        if self.collector.size() >= self.batch_size:
            self._send_batch()

        return item

    def _send_batch(self):
        """Send accumulated data (requests, items, logs) together"""
        data = self.collector.get_and_clear()
        if data:
            try:
                self.client.send_unified_data(data)
            except Exception as e:
                # Log error but don't lose data - keep it for retry
                pass

    def spider_closed(self, spider):
        """Send any remaining data when spider closes"""
        self._send_batch()
