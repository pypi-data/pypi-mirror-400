# APCloudy Pipeline

A high-performance Scrapy integration that sends **items, requests, logs, and spider statistics** to your backend using **unified batch processing** and **secure HMAC-based authentication**.

---

## ✨ Features

- 📦 **Unified Data Sending** - All data (items, requests, logs, stats) sent in a single API call
- 🚀 **Batch Processing** - Automatic batching every 10 items or on spider close
- 🌐 **Complete Request Tracking** - Logs both successful and failed requests with detailed error information
- 📊 **Spider Statistics** - Comprehensive spider performance metrics
- 🧾 **Log Forwarding** - Captures spider, user, and Scrapy internal logs
- 🔐 **Secure Authentication** - HMAC-SHA256 signature-based API communication
- ⚡ **High Performance** - Thread-safe data collection with minimal overhead
- 🎯 **Zero Configuration** - Works out of the box with sensible defaults

---

## 📦 Installation

```bash
pip install apcloudy-pipeline
```

---

## ⚙️ Configuration

Add the following settings to your Scrapy project's `settings.py` file:

```python
# Required: API credentials
APCLOUDY_URL = "https://your-api.com"  # Base URL (webhook path added automatically)
APCLOUDY_API_KEY = "your_public_api_key"
APCLOUDY_SECRET_KEY = "your_secret_key"
JOB_ID = 123  # Can also be passed via spider args

# Optional: Batch size (default: 10)
APCLOUDY_BATCH_SIZE = 10  # Send data every 10 items

# Required: Item Pipeline
ITEM_PIPELINES = {
    "apcloudy_pipeline.pipelines.APCloudyItemPipeline": 300,
}

# Required: Error Middleware (to catch failed requests)
DOWNLOADER_MIDDLEWARES = {
    'apcloudy_pipeline.middleware.APCloudyErrorMiddleware': 50,
    # ... your other middlewares
}

# Required: Extensions for request logging, logs, and stats
EXTENSIONS = {
    "apcloudy_pipeline.request_logger.APCloudyRequestLogger": 100,
    "apcloudy_pipeline.extensions.APCloudyLoggingExtension": 100,
    "apcloudy_pipeline.extensions.APCloudyStatsExtension": 100,
}
```

---

## 🏗️ Architecture

### Data Flow

```
┌──────────────────────────────────────────────────────────┐
│                    SPIDER EXECUTION                       │
└──────────────────────────────────────────────────────────┘
                         ↓
    ┌────────────────────┼────────────────────┐
    ↓                    ↓                     ↓
┌─────────┐      ┌──────────┐         ┌──────────┐
│Requests │      │  Items   │         │   Logs   │
└─────────┘      └──────────┘         └──────────┘
    ↓                    ↓                     ↓
    └────────────────────┼─────────────────────┘
                         ↓
              ┌──────────────────┐
              │  DataCollector   │
              │  (Thread-Safe)   │
              └──────────────────┘
                         ↓
              ┌──────────────────┐
              │ Batch Trigger?   │
              │ • 10+ items      │
              │ • Spider closes  │
              └──────────────────┘
                         ↓
              ┌──────────────────┐
              │  APCloudyClient  │
              │  (HMAC Auth)     │
              └──────────────────┘
                         ↓
              ┌──────────────────┐
              │      Backend     │
              │   (Unified API)  │
              └──────────────────┘
```

---

## 📡 API Payload Structure

All data is sent in a single unified payload:

```json
{
  "job_id": "123",
  "data": {
    "requests": [
      {
        "url": "https://example.com/product",
        "method": "GET",
        "status_code": 200,
        "response_time": 1.23,
        "fingerprint": "f3045685b89f920b3faefc7d3df2d3c88bdab393",
        "error": null,
        "success": true
      },
      {
        "url": "https://example.com/error",
        "method": "GET",
        "status_code": 400,
        "response_time": 0.45,
        "fingerprint": "a1b2c3d4e5f6...",
        "error": "AskPablosAPIError: [400] Invalid JSON format",
        "success": false
      }
    ],
    "items": [
      {
        "title": "Product Name",
        "price": "99.99",
        "url": "https://example.com/product"
      }
    ],
    "logs": [
      {
        "level": "INFO",
        "message": "Spider started",
        "exception": null
      },
      {
        "level": "ERROR",
        "message": "Failed to parse page",
        "exception": "Traceback..."
      }
    ],
    "stats": {
      "item_scraped_count": 1,
      "request_count": 2,
      "response_received_count": 1,
      "downloader/exception_count": 1,
      "finish_time": "2026-01-06T11:28:46",
      "finish_reason": "finished"
    }
  }
}
```

---

## 🔧 Components

### 1. **APCloudyItemPipeline**
- Collects scraped items
- Triggers batch send every 10 items
- Sends remaining items on spider close

### 2. **APCloudyRequestLogger**
- Logs successful HTTP responses (including non-200 status codes)
- Tracks response time for each request
- Generates unique fingerprints for requests

### 3. **APCloudyErrorMiddleware**
- Captures failed requests and exceptions
- Extracts HTTP status codes from error messages
- Logs middleware errors (API errors, timeouts, network failures)

### 4. **APCloudyLoggingExtension**
- Captures all Python logging output
- Forwards spider, user, and Scrapy internal logs
- Includes exception tracebacks

### 5. **APCloudyStatsExtension**
- Collects comprehensive spider statistics
- Sent once at spider close
- Includes item counts, request metrics, timing, etc.

### 6. **DataCollector**
- Thread-safe central data storage
- Shared across all components
- Batches data before sending

### 7. **APCloudyClient**
- Handles HMAC-SHA256 authentication
- Sends unified data to backend
- Automatic signature generation

---

## 🔐 Authentication

The package uses HMAC-SHA256 for secure API communication:

**Headers:**
```
X-API-KEY: {your_public_key}
X-TIMESTAMP: {unix_timestamp}
X-SIGNATURE: {hmac_sha256(secret_key, timestamp + "." + json_body)}
Content-Type: application/json
```

**Signature Calculation:**
```python
message = f"{timestamp}.{json_body}"
signature = HMAC_SHA256(secret_key, message)
```

---

## 🚀 Performance

- **Reduced API Calls**: 1 request per batch instead of N individual requests
- **Configurable Batch Size**: Set `APCLOUDY_BATCH_SIZE` in settings (default: 10 items)
- **Thread-Safe**: Handles concurrent data collection safely
- **Minimal Overhead**: Efficient data collection with locks

---

## 📋 Requirements

- Python 3.8+
- Scrapy 2.0+
- requests

---

## 🛠️ Advanced Configuration

### Custom Batch Size

Control when data is sent by adjusting the batch size:

```python
# Send every 50 items
APCLOUDY_BATCH_SIZE = 50

# Send every 100 items
APCLOUDY_BATCH_SIZE = 100

# Send immediately (batch size of 1)
APCLOUDY_BATCH_SIZE = 1
```

**Note**: Data is always sent when the spider closes, regardless of batch size.

### Custom Job ID via Spider Args

```python
scrapy crawl myspider -a JOB_ID=456
```

### Backend Endpoint

The package automatically appends `/api/webhook/consume` to your base URL:

```
Base URL: https://your-api.com
Full endpoint: https://your-api.com/api/webhook/consume
```

Data is sent via:
```
POST {APCLOUDY_URL}/api/webhook/consume
```

Make sure your backend handles the unified payload structure at this endpoint.

---

## 📝 Example Spider

```python
import scrapy

class MySpider(scrapy.Spider):
    name = 'myspider'

    def start_requests(self):
        urls = ['https://example.com/page1', 'https://example.com/page2']
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        yield {
            'title': response.css('h1::text').get(),
            'price': response.css('.price::text').get(),
            'url': response.url
        }
```

**No changes needed to your spider code!** The pipeline automatically collects and sends all data.

---

## 🐛 Troubleshooting

### Data Not Being Sent

1. Check that all required settings are configured
2. Verify API credentials are correct
3. Ensure middleware and extensions are enabled
4. Check logs for error messages

### Failed Requests Not Being Logged

1. Ensure `APCloudyErrorMiddleware` is added to `DOWNLOADER_MIDDLEWARES`
2. Check middleware priority (should be < 100 to catch errors early)

### Stats Not Included

1. Verify `APCloudyStatsExtension` is enabled in `EXTENSIONS`
2. Stats are only sent once at spider close

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and questions, please open an issue on GitHub.
