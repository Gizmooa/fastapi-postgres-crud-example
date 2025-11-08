# API Versioning
API_VERSION = "v1"  # Current API version
API_VERSION_PREFIX = f"/{API_VERSION}"  # URL prefix for current version

# Pagination defaults
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Database connection pool settings
DB_POOL_SIZE = 10  # Number of connections to maintain in the pool
DB_MAX_OVERFLOW = 20  # Maximum number of connections beyond pool_size
DB_POOL_RECYCLE_SECONDS = 3600  # Recycle connections after 1 hour (in seconds)
