"""Constants and configuration values for the MixBridge calculator system."""

# Calculation constants
BASIS_POINTS_MULTIPLIER = 10000
DEFAULT_DECIMAL_PLACES = 4

# Metric categories
VOLUME_METRICS = [
    'clicks', 'impressions', 'video_views', 'engagements',
    'landing_page_views', 'link_clicks', 'outbound_clicks',
    'post_engagements', 'page_engagements', 'conversions', 
    'video_p100_views', 'reach', 'frequency'
]

RATE_METRICS = [
    'CTR', 'VTR', 'ER', 'LPER', 'LER', 'OLER', 'PER', 
    'PGER', 'CVR', 'CPM', 'VCR', 'CPC', 'CPLPV', 'CPE', 
    'CPPGE', 'CPV', 'cost_per_conversion', 'engagement_rate'
]

COST_METRICS = ['spend']

ALL_METRICS = VOLUME_METRICS + RATE_METRICS + COST_METRICS

# File operation constants
DEFAULT_ENCODING = 'utf-8'
CSV_BUFFER_SIZE = 1024 * 1024  # 1MB buffer for CSV operations

# Validation constants
MIN_CONFIDENCE_LEVEL = 0.0
ZERO_TOLERANCE = 1e-10
PERCENTAGE_TOLERANCE = 0.01
MAX_CONFIDENCE_LEVEL = 100.0
DEFAULT_CONFIDENCE_LEVEL = 90.0

# Tolerance values
ZERO_TOLERANCE = 1e-10
PERCENTAGE_TOLERANCE = 0.0001  # 0.01% tolerance for percentage comparisons

# Default values
DEFAULT_DATE_COLUMN = 'Date'
DEFAULT_CAMPAIGN_COLUMN = 'Campaign Name'
DEFAULT_SPEND_COLUMN = 'spend'

# Performance thresholds
MAX_ROWS_FOR_ITERROWS = 1000  # Switch to vectorized operations above this
CHUNK_SIZE = 10000  # For processing large datasets

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'