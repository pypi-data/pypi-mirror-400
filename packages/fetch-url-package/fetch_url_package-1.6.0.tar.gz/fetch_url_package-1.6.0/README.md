# fetch-url-package

Professional web content fetching and extraction toolkit with configurable extraction methods, detailed error handling, and domain caching.

## Installation

### Basic Installation

```bash
pip install fetch-url-package
```

### With Trafilatura Support

```bash
pip install fetch-url-package[trafilatura]
```

### Development Installation

```bash
pip install fetch-url-package[dev]
```

## Quick Start

### Simple Usage (Default Simple Extractor)

```python
from fetch_url_package import fetch

# Fetch and extract content with default settings
result = fetch("https://example.com")

if result.success:
    print("Content:", result.content)
else:
    print(f"Error ({result.error_type}): {result.error_message}")
```

### Using Trafilatura Extractor

```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod

config = FetchConfig(
    extraction_method=ExtractionMethod.TRAFILATURA,
    extraction_kwargs={"include_tables": True}
)

result = fetch("https://example.com", config=config)
if result.success:
    print(result.content)
```

### Fetch HTML Only (No Extraction)

```python
from fetch_url_package import fetch_html

result = fetch_html("https://example.com")
if result.success:
    print("HTML:", result.html)
```

### Using Content Cache

The content cache stores successfully fetched webpage content (HTML and extracted text) to avoid redundant requests. **Optimized for high concurrency with sharding**.

**IMPORTANT**: For cache to persist across multiple fetch calls, you **MUST** create cache instances explicitly and reuse them.

```python
from fetch_url_package import fetch, FetchConfig, create_content_cache

# RECOMMENDED: Create cache instance explicitly (persists across calls)
content_cache = create_content_cache(max_size=500, num_shards=16)
config = FetchConfig(content_cache=content_cache)

# First fetch - will hit the network
result1 = fetch("https://example.com", config=config)

# Second fetch - will use cached content (much faster!)
result2 = fetch("https://example.com", config=config)
print(result2.metadata.get("from_cache"))  # True

# For ultra-high concurrency: increase sharding
# More shards = better concurrency but slightly more memory
high_concurrency_cache = create_content_cache(max_size=1000, num_shards=32)
config_high_perf = FetchConfig(content_cache=high_concurrency_cache)

# Check cache statistics
stats = content_cache.get_stats()
print(f"Cached pages: {stats['total_entries']}/{stats['max_size']}")
print(f"Shards: {stats['num_shards']}")
```

**DEPRECATED (not recommended)**: Using `content_cache_size` parameter auto-creates a new cache each time, which doesn't persist:

```python
# WARNING: This creates a NEW cache each time config is created.
# Cache will NOT persist across different config instances.
# This parameter is deprecated and will be removed in version 2.0.
config = FetchConfig(content_cache_size=500)  # Avoid this pattern
```

### Advanced Configuration

```python
from fetch_url_package import (
    fetch, 
    FetchConfig, 
    ExtractionMethod,
    create_content_cache,
    create_domain_cache,
)

# Create cache instances using helper functions (RECOMMENDED)
domain_cache = create_domain_cache(
    cache_file="/tmp/fetch_cache.json",
    ttl=86400,  # 24 hours
    failure_threshold=3
)

content_cache = create_content_cache(max_size=1000, num_shards=16)

# Configure fetch settings
config = FetchConfig(
    # Retry settings
    max_retries=5,
    retry_delay=2.0,
    
    # Timeout settings (fine-grained control)
    timeout=60.0,           # Default for read, write, pool
    connect_timeout=15.0,   # Connection establishment
    read_timeout=45.0,      # Reading response data (optional, uses timeout if not set)
    write_timeout=30.0,     # Writing request data (optional, uses timeout if not set)
    pool_timeout=10.0,      # Acquiring connection from pool (optional, uses timeout if not set)
    
    # Proxy settings (randomly selected for each request)
    proxies=[
        "http://user:pass@proxy1.example.com:8080",
        "http://user:pass@proxy2.example.com:8080",
    ],
    
    # Extraction settings
    extraction_method=ExtractionMethod.SIMPLE,
    
    # Custom headers
    custom_headers={
        "X-Custom-Header": "value"
    },
    
    # Domain cache settings (for failures)
    use_cache=True,
    cache=domain_cache,
    
    # Content cache settings (for successful fetches)
    content_cache=content_cache,
    
    # Return HTML along with extracted content
    return_html=True,
    
    # Blocked domains
    blocked_domains=["example-blocked.com"]
)

result = fetch("https://example.com", config=config)
```

### Multi-Process and Multi-Threaded Usage

For high-concurrency scenarios, the cache system provides optimized performance:

#### Multi-Threaded (Recommended for Most Cases)

```python
from fetch_url_package import fetch, FetchConfig, create_content_cache
from concurrent.futures import ThreadPoolExecutor

# Create a shared cache with high shard count for better concurrency
content_cache = create_content_cache(max_size=1000, num_shards=32)
config = FetchConfig(content_cache=content_cache)

urls = ["url1", "url2", "url3", ...]

def fetch_url(url):
    return fetch(url, config=config)

# All threads share the same cache efficiently
with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(fetch_url, urls))
```

**Shard Count Guidelines:**
- Low concurrency (1-10 threads): `num_shards=16` (default)
- Medium concurrency (10-50 threads): `num_shards=32`
- High concurrency (50-200 threads): `num_shards=64`
- Very high concurrency (200+ threads): `num_shards=128`

#### Multi-Process

For ProcessPoolExecutor, use worker initializer to create cache per worker:

```python
from fetch_url_package import fetch, FetchConfig, create_content_cache
from concurrent.futures import ProcessPoolExecutor

# Global variables for worker processes
worker_cache = None
worker_config = None

def worker_init():
    """Initialize cache once per worker process."""
    global worker_cache, worker_config
    worker_cache = create_content_cache(max_size=500, num_shards=16)
    worker_config = FetchConfig(content_cache=worker_cache)

def fetch_url(url):
    return fetch(url, config=worker_config)

urls = ["url1", "url2", "url3", ...]

# Each worker process has its own cache
with ProcessPoolExecutor(max_workers=4, initializer=worker_init) as executor:
    results = list(executor.map(fetch_url, urls))
```

See `example_multiprocess.py` for complete examples.

## API Reference

### Helper Functions

#### `create_content_cache(max_size=500, num_shards=16)`

Create a ContentCache instance with recommended defaults.

**Parameters:**
- `max_size` (int): Maximum number of entries to cache (default: 500)
- `num_shards` (int): Number of cache shards for concurrency (default: 16)

**Returns:** `ContentCache` instance

#### `create_domain_cache(cache_file=None, ttl=86400, failure_threshold=3, max_size=10000)`

Create a DomainCache instance with recommended defaults.

**Parameters:**
- `cache_file` (str, optional): Path to cache file for persistence
- `ttl` (int): Time-to-live for cache entries in seconds (default: 86400)
- `failure_threshold` (int): Number of failures before caching (default: 3)
- `max_size` (int): Maximum cache entries (default: 10000)

**Returns:** `DomainCache` instance

### Main Functions

#### `fetch(url, config=None, extract=True)`
#### `fetch_async(url, config=None, extract=True)`

Fetch and optionally extract content from URL.

**Parameters:**
- `url` (str): URL to fetch
- `config` (FetchConfig, optional): Configuration object
- `extract` (bool): Whether to extract content (default: True)

**Returns:** `FetchResult` object

#### `fetch_html(url, config=None)`

Fetch HTML content only without extraction.

**Parameters:**
- `url` (str): URL to fetch
- `config` (FetchConfig, optional): Configuration object

**Returns:** `FetchResult` object

### Configuration Classes

#### `FetchConfig`

Configuration for fetch operations.

**Parameters:**
- `max_retries` (int): Maximum retry attempts (default: 3)
- `retry_delay` (float): Base delay between retries in seconds (default: 1.0)
- `timeout` (float): Default timeout for all operations (read, write, pool) in seconds (default: 30.0)
- `connect_timeout` (float): Connection timeout in seconds (default: 10.0)
- `read_timeout` (float, optional): Read timeout in seconds (uses `timeout` if None)
- `write_timeout` (float, optional): Write timeout in seconds (uses `timeout` if None)
- `pool_timeout` (float, optional): Pool timeout for acquiring connections in seconds (uses `timeout` if None)
- `follow_redirects` (bool): Follow HTTP redirects (default: True)
- `max_redirects` (int): Maximum number of redirects (default: 10)
- `http2` (bool): Use HTTP/2 (default: True)
- `verify_ssl` (bool): Verify SSL certificates (default: False)
- `user_agents` (List[str], optional): List of user agents to rotate
- `referers` (List[str], optional): List of referers to rotate
- `custom_headers` (Dict[str, str], optional): Custom HTTP headers
- `proxies` (List[str], optional): List of proxy URLs (format: `http://user:pass@host:port`). A random proxy is selected for each request.
- `extraction_method` (ExtractionMethod): Extraction method (default: SIMPLE)
- `extraction_kwargs` (Dict): Additional arguments for extractor
- `filter_file_extensions` (bool): Filter file URLs (default: True)
- `blocked_domains` (List[str], optional): Domains to block
- `use_cache` (bool): Use domain cache for failed domains (default: False)
- `cache` (DomainCache, optional): Domain cache instance for failed domains (create with `create_domain_cache()`)
- `content_cache_size` (int): **DEPRECATED** - Size of content cache (default: 0, disabled). Use `content_cache` parameter instead for cache persistence.
- `content_cache` (ContentCache, optional): Content cache instance for successful fetches (create with `create_content_cache()`)
- `return_html` (bool): Include HTML in result (default: False)

**Important:** To ensure cache persists across multiple fetch calls, always create cache instances explicitly using `create_content_cache()` or `create_domain_cache()` and pass them to the config. Do not rely on auto-creation via `content_cache_size`.

#### `DomainCache`

Cache for tracking failed domains to avoid repeated failures.

**Parameters:**
- `cache_file` (str, optional): Path to cache file for persistence
- `ttl` (int): Time-to-live for cache entries in seconds (default: 86400)
- `failure_threshold` (int): Failures before caching domain (default: 3)
- `max_size` (int): Maximum cache entries (default: 10000)

**Methods:**
- `should_skip(url)`: Check if URL should be skipped
- `record_failure(url, error_type)`: Record a failure
- `record_success(url)`: Record a success
- `clear()`: Clear all cache entries
- `get_stats()`: Get cache statistics

#### `ContentCache`

High-performance LRU cache for storing successfully fetched webpage content (both HTML and extracted text).

**Parameters:**
- `max_size` (int): Maximum number of entries to cache (default: 500)
- `num_shards` (int): Number of cache shards for concurrency (default: 16)

**Features:**
- LRU (Least Recently Used) eviction policy
- **Optimized for high concurrency** with sharding to reduce lock contention
- Stores both HTML and extracted content
- Only caches successful fetches (not failures)
- Thread-safe operations with minimal blocking
- Short-term temporary cache for performance optimization

**Concurrency Optimization:**
The cache uses sharding to minimize lock contention under high concurrency. URLs are distributed across multiple shards based on hash, allowing concurrent operations on different URLs to proceed in parallel without blocking each other. This design supports thousands of concurrent requests efficiently.

**Methods:**
- `get(url)`: Get cached content for a URL
- `put(url, html, content, final_url, metadata)`: Store content in cache
- `clear()`: Clear all cache entries
- `get_stats()`: Get cache statistics

### Result Classes

#### `FetchResult`

Result object containing fetch outcome and data.

**Attributes:**
- `url` (str): Original URL
- `success` (bool): Whether fetch was successful
- `content` (str, optional): Extracted content
- `html` (str, optional): Raw HTML content
- `error_type` (ErrorType, optional): Type of error if failed
- `error_message` (str, optional): Error message if failed
- `status_code` (int, optional): HTTP status code
- `final_url` (str, optional): Final URL after redirects
- `metadata` (Dict): Additional metadata

### Extraction Methods

#### `ExtractionMethod.SIMPLE` (Default)

Simple and fast extraction that removes HTML/XML tags without complex parsing.

**Pros:**
- No external dependencies
- Fast performance
- Reliable for most web pages

**Cons:**
- Less sophisticated than trafilatura
- May include some unwanted content

#### `ExtractionMethod.TRAFILATURA`

Advanced extraction using the trafilatura library.

**Pros:**
- Better content extraction quality
- Filters out navigation, ads, etc.
- Handles complex page structures

**Cons:**
- Requires trafilatura dependency
- Slightly slower

## Error Types

The package provides detailed error types:

- `NOT_FOUND` (404): Page not found
- `FORBIDDEN` (403): Access denied
- `RATE_LIMITED` (429): Too many requests
- `SERVER_ERROR` (5xx): Server error
- `TIMEOUT`: Request timeout
- `NETWORK_ERROR`: Network/connection error
- `SSL_ERROR`: SSL/TLS error
- `FILTERED`: URL filtered by configuration
- `EMPTY_CONTENT`: Page returned empty content
- `EXTRACTION_FAILED`: Content extraction failed
- `CACHED_FAILURE`: Domain in failure cache
- `UNKNOWN`: Unknown error

## Best Practices & Recommendations

### 1. Bypassing Human Verification (CAPTCHA)

**Challenge:** Many websites use CAPTCHA or human verification to block automated requests.

**Recommendations:**

1. **Use Proxy Services**: Consider using services like:
   - Oxylabs (already referenced in your code)
   - ScraperAPI
   - Bright Data (formerly Luminati)

2. **Implement Delays**: Add random delays between requests
   ```python
   import time
   import random
   
   for url in urls:
       result = fetch(url)
       time.sleep(random.uniform(2, 5))  # 2-5 second delay
   ```

3. **Rotate User Agents**: Already built-in, but you can add more
   ```python
   config = FetchConfig(
       user_agents=[
           "Your custom user agent 1",
           "Your custom user agent 2",
       ]
   )
   ```

4. **Use Sessions**: For multiple requests to same domain
   ```python
   # Future enhancement - session management
   ```

5. **Selenium/Playwright**: For JavaScript-heavy sites (not included in this package)

### 2. Handling Redirects

The package automatically handles:
- HTTP redirects (301, 302, 307, 308)
- Meta refresh redirects
- JavaScript redirects (partial support)

**Configuration:**
```python
config = FetchConfig(
    follow_redirects=True,
    max_redirects=10  # Adjust as needed
)
```

**For Complex JavaScript Redirects:**
Consider using browser automation tools like Selenium or Playwright for pages that heavily rely on JavaScript.

### 3. Domain Caching Strategy

**Use Cases:**
- Large-scale scraping operations
- Batch URL processing
- Avoiding repeated failures

**Example:**
```python
from fetch_url_package import DomainCache, FetchConfig, fetch

# Persistent cache
cache = DomainCache(
    cache_file="/var/cache/fetch_domains.json",
    ttl=86400,  # 24 hours
    failure_threshold=3  # Cache after 3 failures
)

config = FetchConfig(use_cache=True, cache=cache)

# Fetch multiple URLs
urls = ["http://example1.com", "http://example2.com"]
for url in urls:
    result = fetch(url, config=config)
    if result.error_type == "cached_failure":
        print(f"Skipped cached domain: {url}")
```

**Cache Statistics:**
```python
stats = cache.get_stats()
print(f"Cached domains: {stats['total_entries']}")
print(f"Domains: {stats['domains']}")
```

### 4. Rate Limiting

**Implement Your Own Rate Limiting:**
```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_second=1):
        self.rps = requests_per_second
        self.last_request = defaultdict(float)
    
    def wait_if_needed(self, domain):
        now = time.time()
        elapsed = now - self.last_request[domain]
        if elapsed < (1.0 / self.rps):
            time.sleep((1.0 / self.rps) - elapsed)
        self.last_request[domain] = time.time()

# Usage
limiter = RateLimiter(requests_per_second=2)
for url in urls:
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    limiter.wait_if_needed(domain)
    result = fetch(url)
```

### 5. Concurrent Fetching

**Using ThreadPoolExecutor:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from fetch_url_package import fetch, FetchConfig

def fetch_url(url):
    return fetch(url)

urls = ["http://example1.com", "http://example2.com", "http://example3.com"]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_url, url): url for url in urls}
    
    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()
            if result.success:
                print(f"Success: {url}")
            else:
                print(f"Failed: {url} - {result.error_message}")
        except Exception as e:
            print(f"Exception: {url} - {e}")
```

### 6. Custom Proxy Support

The package now supports HTTP/HTTPS proxy servers with authentication. You can provide a list of proxy URLs, and a random proxy will be selected for each request.

**Using HTTP Proxy:**
```python
from fetch_url_package import fetch, FetchConfig

# Single proxy
config = FetchConfig(
    proxies=["http://username:password@proxy.example.com:8080"]
)
result = fetch("https://example.com", config=config)

# Multiple proxies (randomly selected for each request)
config = FetchConfig(
    proxies=[
        "http://user1:pass1@proxy1.example.com:8080",
        "http://user2:pass2@proxy2.example.com:8080",
        "http://user3:pass3@proxy3.example.com:8080",
    ]
)
result = fetch("https://example.com", config=config)

# Proxy without authentication
config = FetchConfig(
    proxies=["http://proxy.example.com:8080"]
)
result = fetch("https://example.com", config=config)
```

**Proxy URL Format:**
- With authentication: `http://username:password@host:port`
- Without authentication: `http://host:port`
- HTTPS proxies: `https://username:password@host:port`

**Note:** If your password contains special characters (like `@`, `:`, or `/`), you need to URL-encode them. For example:
- `@` should be encoded as `%40`
- `:` should be encoded as `%3A`
- Example: `http://user:p%40ssw0rd@proxy.com:8080` for password `p@ssw0rd`

**Benefits of Multiple Proxies:**
- Load distribution across proxy servers
- Automatic failover if one proxy fails
- Rate limit avoidance by rotating proxies
```

### 7. Handling Different Content Types

**Check Response Content:**
```python
result = fetch_html("https://example.com")
if result.success and result.html:
    # Check if it's actually HTML
    if result.html.strip().startswith('<!DOCTYPE') or '<html' in result.html.lower():
        # Process HTML
        pass
```

## Examples

### Example 1: Simple Content Extraction

```python
from fetch_url_package import fetch

result = fetch("https://en.wikipedia.org/wiki/Python_(programming_language)")
if result.success:
    print(f"Extracted {len(result.content)} characters")
    print(result.content[:500])  # First 500 characters
else:
    print(f"Error: {result.error_message}")
```

### Example 2: Using Content Cache for Performance

```python
from fetch_url_package import fetch, FetchConfig
import time

# Enable content cache
config = FetchConfig(content_cache_size=500)

urls = [
    "https://example.com",
    "https://example.com",  # Duplicate - will use cache
    "https://example.com",  # Duplicate - will use cache
]

for i, url in enumerate(urls, 1):
    start = time.time()
    result = fetch(url, config=config)
    elapsed = time.time() - start
    
    if result.success:
        from_cache = result.metadata.get("from_cache", False)
        print(f"Fetch {i}: {elapsed:.3f}s (cached: {from_cache})")

# Check cache stats
if config.content_cache:
    stats = config.content_cache.get_stats()
    print(f"Cache: {stats['total_entries']} entries")
```

### Example 3: Batch Processing with Domain Cache

```python
from fetch_url_package import fetch, FetchConfig, DomainCache

cache = DomainCache(cache_file="batch_cache.json")
config = FetchConfig(use_cache=True, cache=cache)

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

results = []
for url in urls:
    result = fetch(url, config=config)
    results.append(result)

# Check cache stats
print(cache.get_stats())
```

### Example 4: Custom Extraction

```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod

# Use trafilatura with custom options
config = FetchConfig(
    extraction_method=ExtractionMethod.TRAFILATURA,
    extraction_kwargs={
        "include_tables": True,
        "include_links": True,
        "include_comments": False,
    }
)

result = fetch("https://example.com", config=config)
```

## Migration from Old Code

If you're migrating from the old `fetch_url.py`:

### Old Code:
```python
from fetch_url import fetch_and_extract

content, error = fetch_and_extract(url)
if error:
    print(f"Error: {error}")
else:
    print(content)
```

### New Code:
```python
from fetch_url_package import fetch

result = fetch(url)
if result.success:
    print(result.content)
else:
    print(f"Error: {result.error_message}")
```

### Using Trafilatura (like old default):
```python
from fetch_url_package import fetch, FetchConfig, ExtractionMethod

config = FetchConfig(extraction_method=ExtractionMethod.TRAFILATURA)
result = fetch(url, config=config)
```

## Development

### Running Tests

```bash
pip install -e .[dev]
pytest tests/
```

### Code Formatting

```bash
black fetch_url_package/
flake8 fetch_url_package/
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
