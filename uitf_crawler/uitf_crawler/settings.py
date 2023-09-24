BOT_NAME = "uitf_crawler"

SPIDER_MODULES = ["uitf_crawler.spiders"]
NEWSPIDER_MODULE = "uitf_crawler.spiders"

ROBOTSTXT_OBEY = False

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_DELAY = 0.25

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5    
AUTOTHROTTLE_MAX_DELAY = 60   
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0 

CONCURRENT_REQUESTS = 32

COOKIES_ENABLED = False 

DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
}

RETRY_TIMES = 10
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

EXTENSIONS = {
   'scrapy.extensions.throttle.AutoThrottle': 300,
}

PROXY_MODE = 0
RANDOM_UA_PER_PROXY = True

DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'en',
}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0 
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

LOG_LEVEL = 'INFO'
LOG_STDOUT = True
LOG_SHORT_NAMES = True