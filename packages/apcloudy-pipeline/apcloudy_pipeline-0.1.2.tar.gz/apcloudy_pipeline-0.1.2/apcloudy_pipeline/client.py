import json
import requests
from .utils import get_timestamp, hmac_signature
from .exceptions import APCloudyPipelineError


class APCloudyClient:
    """
    Manages interaction with the AP Cloudy API for sending unified data.

    This class handles API authentication, including signature generation and
    request header management. It ensures that all necessary credential information is
    configured before usage, raising errors otherwise.
    """

    def __init__(self, crawler):
        # Load settings from crawler (includes spider args)
        settings = crawler.settings
        spider = crawler.spider

        self.api_url = settings.get("APCLOUDY_API_URL")
        self.public_key = settings.get("APCLOUDY_API_KEY")
        self.secret_key = settings.get("APCLOUDY_SECRET_KEY")
        # Get JOB_ID from spider args first, fallback to settings
        self.job_id = getattr(spider, 'JOB_ID', None) or settings.get("JOB_ID")

        if not all([self.api_url, self.public_key, self.secret_key, self.job_id]):
            raise APCloudyPipelineError(
                "APCloudy API credentials not found in Scrapy settings"
            )

    def _post(self, payload: dict):
        """
        Sends a POST request with unified data payload.

        Constructs authenticated request with HMAC signature and sends
        to the AP Cloudy API endpoint.
        """
        raw_body = json.dumps(payload)
        timestamp = get_timestamp()
        signature = hmac_signature(self.secret_key, raw_body, timestamp)

        headers = {
            "X-API-KEY": self.public_key,
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": signature,
            "Content-Type": "application/json"
        }

        try:
            r = requests.post(self.api_url, headers=headers, data=raw_body, timeout=10)
            r.raise_for_status()
        except Exception as e:
            raise APCloudyPipelineError(f"Failed to send data to AP Cloudy backend: {e}")

    def send_unified_data(self, data: dict):
        """
        Send unified data containing requests, items, logs, and stats in a single call.

        This method accepts a dictionary containing all types of data (requests, items,
        logs, stats) and sends them together to the backend in a single API request.

        Expected data structure:
        {
            "requests": [...],  # list of request logs
            "items": [...],     # list of scraped items
            "logs": [...],      # list of log entries
            "stats": {...}      # statistics dict (optional)
        }
        """
        payload = {"job_id": self.job_id, "data": data}
        return self._post(payload)
