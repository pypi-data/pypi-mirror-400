"""
Main fetch module with configurable fetching and extraction.
"""

import asyncio
import ssl
import random
import logging
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import httpx
from urllib.parse import urlparse, urljoin
import re

from .extractor import extract_content
from .cache import DomainCache, ContentCache
from .text_encoder import parse_encoder

logger = logging.getLogger(__name__)


class ExtractionMethod(str, Enum):
    """Supported extraction methods."""
    SIMPLE = "simple"
    TRAFILATURA = "trafilatura"


class ErrorType(str, Enum):
    """Error types for better error handling."""
    NOT_FOUND = "404"
    FORBIDDEN = "403"
    RATE_LIMITED = "429"
    SERVER_ERROR = "5xx"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network"
    SSL_ERROR = "ssl"
    FILTERED = "filtered"
    EMPTY_CONTENT = "empty"
    EXTRACTION_FAILED = "extraction_failed"
    CACHED_FAILURE = "cached_failure"
    UNKNOWN = "unknown"


@dataclass
class FetchResult:
    """
    Result of a fetch operation with detailed information.
    """
    url: str
    success: bool
    content: Optional[str] = None
    html: Optional[str] = None
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    final_url: Optional[str] = None  # After redirects
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        if self.success:
            content_preview = (self.content[:50] + "...") if self.content and len(self.content) > 50 else self.content
            return f"FetchResult(success=True, url={self.url}, content_length={len(self.content or '')})"
        else:
            return f"FetchResult(success=False, url={self.url}, error_type={self.error_type}, error={self.error_message})"


@dataclass
class FetchConfig:
    """
    Configuration for fetch operations.
    
    Important: For cache persistence across multiple fetch calls, you MUST create
    and pass cache instances explicitly. Do not rely on auto-creation.
    
    Example of correct usage:
        # Create cache instances using helper functions (reuse them across calls)
        content_cache = create_content_cache(max_size=500)
        domain_cache = create_domain_cache()
        
        # Pass to config
        config = FetchConfig(
            content_cache=content_cache,
            use_cache=True,
            cache=domain_cache
        )
        
        # Use the same config for all fetches to maintain cache
        result1 = fetch(url1, config=config)
        result2 = fetch(url2, config=config)  # Uses same cache
    """
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Timeout settings
    timeout: float = 30.0  # Default timeout for read, write, pool operations (when not explicitly set)
    connect_timeout: float = 10.0  # Timeout for establishing connection
    # Optional fine-grained timeouts (None = uses timeout value above)
    read_timeout: Optional[float] = None  # Timeout for reading response data
    write_timeout: Optional[float] = None  # Timeout for writing request data
    pool_timeout: Optional[float] = None  # Timeout for acquiring connection from pool
    
    # Redirect settings
    follow_redirects: bool = True
    max_redirects: int = 10
    
    # HTTP settings
    http2: bool = True
    verify_ssl: bool = False
    
    # Headers and user agents
    user_agents: Optional[List[str]] = None
    referers: Optional[List[str]] = None
    custom_headers: Optional[Dict[str, str]] = None
    
    # Proxy settings
    proxies: Optional[List[str]] = None  # List of proxy URLs (e.g., ["http://user:pass@proxy1:port", ...])
    
    # Extraction settings
    extraction_method: ExtractionMethod = ExtractionMethod.SIMPLE
    extraction_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # Filtering settings
    filter_file_extensions: bool = True
    blocked_domains: Optional[List[str]] = None
    
    # Cache settings (for failed domains)
    use_cache: bool = False
    cache: Optional[DomainCache] = None
    
    # Content cache settings (for successful fetches)
    # DEPRECATED: Use content_cache parameter instead for explicit cache management
    content_cache_size: int = 0  # 0 means disabled, >0 enables with specified size
    content_cache: Optional[ContentCache] = None
    
    # Content settings
    return_html: bool = False  # Whether to include HTML in result
    
    def __post_init__(self):
        """Initialize default values."""
        if self.user_agents is None:
            self.user_agents = DEFAULT_USER_AGENTS
        if self.referers is None:
            self.referers = DEFAULT_REFERERS
        if self.blocked_domains is None:
            self.blocked_domains = []
        
        # Auto-create domain cache only if explicitly requested
        # This maintains backward compatibility but is not recommended
        if self.use_cache and self.cache is None:
            logger.warning(
                "Auto-creating DomainCache. For cache persistence across calls, "
                "create a DomainCache instance and pass it explicitly: "
                "cache = DomainCache(); config = FetchConfig(use_cache=True, cache=cache)"
            )
            self.cache = DomainCache()
        
        # Auto-create content cache only if size specified but no cache provided
        # This is DEPRECATED and will be removed in future versions
        if self.content_cache_size > 0 and self.content_cache is None:
            logger.warning(
                "DEPRECATED: content_cache_size parameter will not persist cache across calls. "
                "For cache persistence, create a ContentCache instance and pass it explicitly: "
                "content_cache = ContentCache(max_size=500); "
                "config = FetchConfig(content_cache=content_cache). "
                "See documentation for examples."
            )
            self.content_cache = ContentCache(max_size=self.content_cache_size)


# Default User-Agents
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

DEFAULT_REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.baidu.com/",
    "",  # Direct access
]


def _get_random_headers(url: str, config: FetchConfig) -> Dict[str, str]:
    """Generate randomized browser-like headers."""
    parsed = urlparse(url)
    
    headers = {
        "User-Agent": random.choice(config.user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site" if random.choice(config.referers) else "none",
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Cache-Control": "max-age=0",
        "Referer": random.choice(config.referers),
        "Host": parsed.netloc,
    }
    
    # Add custom headers if provided
    if config.custom_headers:
        headers.update(config.custom_headers)
    
    return headers


def _create_ssl_context() -> ssl.SSLContext:
    """Create a permissive SSL context for compatibility."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.set_ciphers('DEFAULT:@SECLEVEL=1')
    
    # Enable legacy server connect for older servers
    # This corresponds to SSL_OP_LEGACY_SERVER_CONNECT (0x4)
    LEGACY_SERVER_CONNECT = 0x4
    try:
        ssl_context.options |= LEGACY_SERVER_CONNECT
    except Exception:
        pass
    return ssl_context


def _should_filter_url(url: str, config: FetchConfig) -> Tuple[bool, Optional[str]]:
    """
    Check if URL should be filtered.
    
    Returns:
        Tuple of (should_filter, reason)
    """
    parsed = urlparse(url)
    
    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        return True, f"Unsupported URL scheme: {parsed.scheme}"
    
    # Check file extensions
    if config.filter_file_extensions:
        # Match file extensions at the end of path (before query string)
        file_pattern = re.compile(
            r'.*\.(pdf|csv|docx|xlsx|zip|rar|exe|jpg|png|gif|mp4|mp3|avi|mov|wav)(\?.*)?$',
            re.IGNORECASE
        )
        if file_pattern.match(parsed.path) or file_pattern.match(url):
            return True, "URL points to a file (not a web page)"
    
    # Check blocked domains
    if config.blocked_domains:
        for blocked_domain in config.blocked_domains:
            if blocked_domain in parsed.netloc:
                return True, f"Domain is blocked: {blocked_domain}"
    
    return False, None


async def fetch_html_async(
    url: str,
    config: Optional[FetchConfig] = None
) -> FetchResult:
    """
    Fetch HTML content from URL with comprehensive error handling.
    
    Args:
        url: URL to fetch
        config: Fetch configuration (uses defaults if None)
    
    Returns:
        FetchResult with HTML content or error information
    """
    if config is None:
        config = FetchConfig()
    
    # Check content cache first (for successful fetches)
    if config.content_cache:
        try:
            cached_entry = config.content_cache.get(url)
            if cached_entry:
                return FetchResult(
                    url=url,
                    success=True,
                    html=cached_entry.html,
                    status_code=200,
                    final_url=cached_entry.final_url,
                    metadata={
                        **cached_entry.metadata,
                        "from_cache": True,
                        "cached_at": cached_entry.timestamp
                    }
                )
        except Exception as e:
            logger.warning(f"Error reading from content cache: {e}")
    
    # Check failure cache
    if config.use_cache and config.cache and config.cache.should_skip(url):
        return FetchResult(
            url=url,
            success=False,
            error_type=ErrorType.CACHED_FAILURE,
            error_message="URL is in failure cache, skipping fetch",
        )
    
    # Check if URL should be filtered
    try:
        should_filter, filter_reason = _should_filter_url(url, config)
    except Exception as e:
        filter_reason = f"Error during URL filtering: {e}"
        logger.warning(filter_reason)
        should_filter = True
    if should_filter:
        return FetchResult(
            url=url,
            success=False,
            error_type=ErrorType.FILTERED,
            error_message=filter_reason,
        )
    
    ssl_context = _create_ssl_context() if not config.verify_ssl else None
    cookies = httpx.Cookies()
    retry_delay = config.retry_delay
    last_error = None
    last_error_type = ErrorType.UNKNOWN
    
    for attempt in range(config.max_retries):
        try:
            # Delay between retries
            if attempt > 0:
                delay = retry_delay * attempt + random.uniform(0.5, 1.5)
                await asyncio.sleep(delay)
            
            headers = _get_random_headers(url, config)
            
            # Select a random proxy if configured
            proxy = None
            if config.proxies:
                proxy = random.choice(config.proxies)
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                    config.timeout,
                    connect=config.connect_timeout,
                    read=config.read_timeout or config.timeout,
                    write=config.write_timeout or config.timeout,
                    pool=config.pool_timeout or config.timeout,
                ),
                follow_redirects=config.follow_redirects,
                max_redirects=config.max_redirects,
                http2=config.http2,
                verify=ssl_context if ssl_context else config.verify_ssl,
                cookies=cookies,
                proxy=proxy,
            ) as client:
                # Warm up with HEAD request on first attempt
                if attempt == 0:
                    try:
                        await client.head(url, headers=headers)
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                    except Exception:
                        pass
                
                response = await client.get(url, headers=headers)
                
                # Handle successful response
                if response.status_code == 200:
                    html = await parse_encoder(response)
                    final_url = str(response.url)
                    
                    # Check for meta refresh redirect
                    meta_refresh = re.search(
                        r'<meta[^>]*http-equiv=["\']?refresh["\']?[^>]*content=["\']?\d+;\s*url=([^"\'\s>]+)',
                        html, re.IGNORECASE
                    )
                    if meta_refresh:
                        redirect_url = meta_refresh.group(1)
                        if not redirect_url.startswith('http'):
                            redirect_url = urljoin(url, redirect_url)
                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        response = await client.get(redirect_url, headers=_get_random_headers(redirect_url, config))
                        html = response.text
                        final_url = str(response.url)
                    
                    # Check for empty content
                    if not html or not html.strip():
                        if config.use_cache and config.cache:
                            config.cache.record_failure(url, ErrorType.EMPTY_CONTENT)
                        return FetchResult(
                            url=url,
                            success=False,
                            error_type=ErrorType.EMPTY_CONTENT,
                            error_message="Page returned empty content",
                            status_code=200,
                            final_url=final_url,
                        )
                    
                    # Success!
                    if config.use_cache and config.cache:
                        config.cache.record_success(url)
                    
                    # Store in content cache
                    if config.content_cache:
                        try:
                            config.content_cache.put(
                                url=url,
                                html=html,
                                final_url=final_url,
                                metadata={
                                    "content_length": len(html),
                                    "redirected": final_url != url,
                                }
                            )
                        except Exception as e:
                            logger.warning(f"Error storing in content cache: {e}")
                    
                    cookies.update(response.cookies)
                    return FetchResult(
                        url=url,
                        success=True,
                        html=html,
                        status_code=200,
                        final_url=final_url,
                        metadata={
                            "content_length": len(html),
                            "redirected": final_url != url,
                        }
                    )
                
                response.raise_for_status()
                
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            
            if status == 403:
                last_error_type = ErrorType.FORBIDDEN
                last_error = f"Access denied (HTTP 403). The website is blocking automated requests."
                logger.warning(f"HTTP 403 for URL {url} (attempt {attempt + 1}/{config.max_retries})")
            elif status == 404:
                last_error_type = ErrorType.NOT_FOUND
                last_error = f"Page not found (HTTP 404). The URL does not exist."
                logger.info(f"HTTP 404 for URL {url}")
                break  # No point retrying 404
            elif status == 429:
                last_error_type = ErrorType.RATE_LIMITED
                last_error = f"Rate limited (HTTP 429). Too many requests."
                logger.warning(f"Rate limited for URL {url}")
                retry_delay = 5.0  # Longer delay for rate limiting
            elif status >= 500:
                last_error_type = ErrorType.SERVER_ERROR
                last_error = f"Server error (HTTP {status}). Please try again later."
                logger.warning(f"Server error {status} for URL {url}")
            else:
                last_error_type = ErrorType.UNKNOWN
                last_error = f"HTTP error {status}"
            
        except httpx.TimeoutException:
            last_error_type = ErrorType.TIMEOUT
            last_error = "Request timeout. The website took too long to respond."
            logger.warning(f"Timeout for URL {url} (attempt {attempt + 1}/{config.max_retries})")
            
        except httpx.RequestError as e:
            last_error_type = ErrorType.NETWORK_ERROR
            last_error = f"Network error: {str(e)}"
            logger.warning(f"Request error for URL {url}: {e}")
            
        except Exception as e:
            last_error_type = ErrorType.UNKNOWN
            last_error = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error fetching URL {url}: {e}")
            break
    
    # All retries failed
    if config.use_cache and config.cache:
        config.cache.record_failure(url, last_error_type.value)
    
    return FetchResult(
        url=url,
        success=False,
        error_type=last_error_type,
        error_message=last_error or "Failed to fetch HTML after all retries",
    )


async def fetch_async(
    url: str,
    config: Optional[FetchConfig] = None,
    extract: bool = True,
) -> FetchResult:
    """
    Fetch and optionally extract content from URL.
    
    Args:
        url: URL to fetch
        config: Fetch configuration (uses defaults if None)
        extract: Whether to extract content (default: True)
    
    Returns:
        FetchResult with extracted content or error information
    """
    if config is None:
        config = FetchConfig()
    
    # Check content cache for extracted content
    if extract and config.content_cache:
        try:
            cached_entry = config.content_cache.get(url)
            if cached_entry and cached_entry.content:
                return FetchResult(
                    url=url,
                    success=True,
                    content=cached_entry.content,
                    html=cached_entry.html if config.return_html else None,
                    status_code=200,
                    final_url=cached_entry.final_url,
                    metadata={
                        **cached_entry.metadata,
                        "from_cache": True,
                        "cached_at": cached_entry.timestamp
                    }
                )
        except Exception as e:
            logger.warning(f"Error reading from content cache: {e}")
    
    # Fetch HTML
    result = await fetch_html_async(url, config)
    
    if not result.success:
        return result
    
    # Extract content if requested
    if extract and result.html:
        try:
            content = extract_content(
                result.html,
                method=config.extraction_method.value,
                **config.extraction_kwargs
            )
            
            if content:
                result.content = content
                result.metadata["extraction_method"] = config.extraction_method.value
                
                # Update content cache with extracted content
                # Note: This may overwrite an existing entry from fetch_html_async,
                # which is intentional - we want to cache the most complete data (HTML + content)
                if config.content_cache:
                    try:
                        config.content_cache.put(
                            url=url,
                            html=result.html,
                            content=content,
                            final_url=result.final_url,
                            metadata=result.metadata
                        )
                    except Exception as e:
                        logger.warning(f"Error storing in content cache: {e}")
                
                # Optionally remove HTML to save memory
                if not config.return_html:
                    result.html = None
            else:
                result.success = False
                result.error_type = ErrorType.EXTRACTION_FAILED
                result.error_message = "Failed to extract readable content from page"
                
                if config.use_cache and config.cache:
                    config.cache.record_failure(url, ErrorType.EXTRACTION_FAILED)
                    
        except Exception as e:
            result.success = False
            result.error_type = ErrorType.EXTRACTION_FAILED
            result.error_message = f"Content extraction failed: {str(e)}"
            
            if config.use_cache and config.cache:
                config.cache.record_failure(url, ErrorType.EXTRACTION_FAILED)
    
    return result


def _run_sync(coro):
    """Run async coroutine synchronously."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop is not None:
        # We're in an async context, create a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


def fetch_html(
    url: str,
    config: Optional[FetchConfig] = None
) -> FetchResult:
    """
    Fetch HTML content from URL (synchronous version).
    
    Args:
        url: URL to fetch
        config: Fetch configuration (uses defaults if None)
    
    Returns:
        FetchResult with HTML content or error information
    """
    return _run_sync(fetch_html_async(url, config))


def fetch(
    url: str,
    config: Optional[FetchConfig] = None,
    extract: bool = True,
) -> FetchResult:
    """
    Fetch and optionally extract content from URL (synchronous version).
    
    Args:
        url: URL to fetch
        config: Fetch configuration (uses defaults if None)
        extract: Whether to extract content (default: True)
    
    Returns:
        FetchResult with extracted content or error information
    
    Examples:
        >>> # Simple fetch with default settings (simple extractor)
        >>> result = fetch("https://example.com")
        >>> if result.success:
        ...     print(result.content)
        
        >>> # Fetch with trafilatura extractor
        >>> config = FetchConfig(extraction_method=ExtractionMethod.TRAFILATURA)
        >>> result = fetch("https://example.com", config=config)
        
        >>> # Fetch with custom settings
        >>> config = FetchConfig(
        ...     max_retries=5,
        ...     timeout=60.0,
        ...     extraction_method=ExtractionMethod.SIMPLE,
        ...     return_html=True,
        ... )
        >>> result = fetch("https://example.com", config=config)
        
        >>> # Fetch without extraction (HTML only)
        >>> result = fetch("https://example.com", extract=False)
        >>> print(result.html)
        
        >>> # Fetch with persistent content cache (RECOMMENDED)
        >>> content_cache = ContentCache(max_size=500)
        >>> config = FetchConfig(content_cache=content_cache)
        >>> result1 = fetch("https://example.com", config=config)
        >>> result2 = fetch("https://example.com", config=config)  # Uses cache
        >>> print(result2.metadata.get("from_cache"))  # True
    """
    return _run_sync(fetch_async(url, config, extract))


# Helper functions for cache creation
def create_content_cache(
    max_size: int = 500,
    num_shards: int = 16
) -> ContentCache:
    """
    Create a ContentCache instance with recommended defaults.
    
    This is a helper function to make cache creation easier and more explicit.
    The created cache should be reused across multiple fetch calls to maintain
    cache persistence.
    
    Args:
        max_size: Maximum number of entries to cache (default: 500)
                 Set to 0 to disable caching
        num_shards: Number of cache shards for concurrency (default: 16)
                   Higher values reduce lock contention in multi-threaded scenarios
                   Recommended values: 16 (default), 32 (high concurrency), 64 (very high)
    
    Returns:
        ContentCache instance ready to use
    
    Examples:
        >>> # Single-threaded or low concurrency
        >>> cache = create_content_cache(max_size=500, num_shards=16)
        >>> config = FetchConfig(content_cache=cache)
        
        >>> # High concurrency (multi-threaded)
        >>> cache = create_content_cache(max_size=1000, num_shards=32)
        >>> config = FetchConfig(content_cache=cache)
        
        >>> # Very high concurrency (hundreds of threads)
        >>> cache = create_content_cache(max_size=2000, num_shards=64)
        >>> config = FetchConfig(content_cache=cache)
        
        >>> # Share cache across multiple configs
        >>> cache = create_content_cache(max_size=500)
        >>> config1 = FetchConfig(content_cache=cache, extraction_method=ExtractionMethod.SIMPLE)
        >>> config2 = FetchConfig(content_cache=cache, extraction_method=ExtractionMethod.TRAFILATURA)
    """
    cache = ContentCache(max_size=max_size, num_shards=num_shards)
    # Initialize shards, to avoid lazy initialization issues
    cache.put(url="Init", 
              html="Init", 
              content="Init", 
              final_url="Init", 
              metadata={})
    return cache


def create_domain_cache(
    cache_file: Optional[str] = None,
    ttl: int = 86400,
    failure_threshold: int = 3,
    max_size: int = 10000
) -> DomainCache:
    """
    Create a DomainCache instance with recommended defaults.
    
    This is a helper function to make cache creation easier and more explicit.
    The created cache should be reused across multiple fetch calls to maintain
    cache persistence.
    
    Args:
        cache_file: Path to cache file for persistence (None for memory-only)
                   Recommended: "/tmp/fetch_domain_cache.json" or similar
        ttl: Time-to-live for cache entries in seconds (default: 86400 = 24 hours)
        failure_threshold: Number of failures before caching URL (default: 3)
        max_size: Maximum number of entries in cache (default: 10000)
    
    Returns:
        DomainCache instance ready to use
    
    Examples:
        >>> # Memory-only cache (for temporary use)
        >>> cache = create_domain_cache()
        >>> config = FetchConfig(use_cache=True, cache=cache)
        
        >>> # Persistent cache (survives process restarts)
        >>> cache = create_domain_cache(cache_file="/tmp/fetch_cache.json")
        >>> config = FetchConfig(use_cache=True, cache=cache)
        
        >>> # Custom settings
        >>> cache = create_domain_cache(
        ...     cache_file="/var/cache/fetch_domains.json",
        ...     ttl=3600,  # 1 hour
        ...     failure_threshold=2  # Cache after 2 failures
        ... )
        >>> config = FetchConfig(use_cache=True, cache=cache)
    """
    return DomainCache(
        cache_file=cache_file,
        ttl=ttl,
        failure_threshold=failure_threshold,
        max_size=max_size
    )
