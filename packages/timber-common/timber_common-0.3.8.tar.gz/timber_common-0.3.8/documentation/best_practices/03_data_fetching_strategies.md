# Data Fetching Strategies - Best Practices

Optimal approaches for fetching, caching, and managing financial data in Timber.

---

## Core Principles

### 1. Fetch Once, Use Many Times
Cache expensive API calls to minimize requests and improve performance.

### 2. Fail Gracefully
Always handle errors and provide fallback mechanisms.

### 3. Respect Rate Limits
Implement delays and batch requests appropriately.

### 4. Validate Input
Check symbols and parameters before making API calls.

### 5. Monitor Data Quality
Verify data integrity and handle missing values.

---

## Fetching Strategies

### Strategy 1: Lazy Loading

Load data only when needed:

```python
class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol
        self._data = None
        self._info = None
    
    @property
    def data(self):
        """Lazy load price data."""
        if self._data is None:
            self._data, error = stock_data_service.fetch_historical_data(
                self.symbol, period='1y'
            )
            if error:
                raise ValueError(f"Failed to fetch data: {error}")
        return self._data
    
    @property
    def info(self):
        """Lazy load company info."""
        if self._info is None:
            self._info, error = stock_data_service.fetch_company_info(self.symbol)
            if error:
                raise ValueError(f"Failed to fetch info: {error}")
        return self._info
    
    def analyze(self):
        """Analyze only loads data when this is called."""
        return {
            'latest_price': self.data['Close'].iloc[-1],
            'company': self.info['longName']
        }

# Usage - data fetched only when needed
analyzer = StockAnalyzer('AAPL')  # No API call yet
result = analyzer.analyze()        # Fetches data now
```

### Strategy 2: Eager Loading

Pre-fetch all required data upfront:

```python
class PortfolioAnalyzer:
    def __init__(self, symbols):
        self.symbols = symbols
        self.data = {}
        self.info = {}
        self._load_all()
    
    def _load_all(self):
        """Pre-fetch all data."""
        for symbol in self.symbols:
            # Load price data
            df, error = stock_data_service.fetch_historical_data(
                symbol, period='1y'
            )
            if not error:
                self.data[symbol] = df
            
            # Load company info
            info, error = stock_data_service.fetch_company_info(symbol)
            if not error:
                self.info[symbol] = info
            
            time.sleep(0.5)  # Rate limiting
    
    def analyze_portfolio(self):
        """All data already loaded."""
        results = {}
        for symbol in self.data:
            results[symbol] = {
                'price': self.data[symbol]['Close'].iloc[-1],
                'name': self.info[symbol]['longName']
            }
        return results

# Usage - all data fetched immediately
analyzer = PortfolioAnalyzer(['AAPL', 'GOOGL', 'MSFT'])
results = analyzer.analyze_portfolio()
```

### Strategy 3: Incremental Loading

Load data in chunks as needed:

```python
class TimeSeriesAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol
        self.periods = ['1mo', '3mo', '1y', '5y']
        self.data_cache = {}
    
    def get_data(self, period):
        """Load data incrementally."""
        if period not in self.data_cache:
            df, error = stock_data_service.fetch_historical_data(
                self.symbol, period=period
            )
            if not error:
                self.data_cache[period] = df
            else:
                return None
        
        return self.data_cache[period]
    
    def analyze_short_term(self):
        """Only loads 1mo data."""
        return self.get_data('1mo')
    
    def analyze_long_term(self):
        """Only loads 5y data when called."""
        return self.get_data('5y')

# Usage - loads only what's needed
analyzer = TimeSeriesAnalyzer('AAPL')
short = analyzer.analyze_short_term()  # Loads 1mo
long = analyzer.analyze_long_term()     # Loads 5y
```

---

## Caching Strategies

### Strategy 1: Time-Based Cache

Cache with expiration:

```python
from datetime import datetime, timedelta
import pickle

class CachedDataFetcher:
    def __init__(self, cache_hours=24):
        self.cache_hours = cache_hours
        self.cache = {}
    
    def _cache_key(self, symbol, period):
        return f"{symbol}_{period}"
    
    def _is_cache_valid(self, timestamp):
        age = datetime.now() - timestamp
        return age < timedelta(hours=self.cache_hours)
    
    def fetch(self, symbol, period='1y'):
        key = self._cache_key(symbol, period)
        
        # Check cache
        if key in self.cache:
            data, timestamp = self.cache[key]
            if self._is_cache_valid(timestamp):
                print(f"Cache hit: {key}")
                return data, None
        
        # Fetch fresh data
        print(f"Cache miss: {key}")
        df, error = stock_data_service.fetch_historical_data(symbol, period)
        
        if not error:
            self.cache[key] = (df, datetime.now())
        
        return df, error
    
    def save_cache(self, filepath):
        """Persist cache to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump(self.cache, f)
    
    def load_cache(self, filepath):
        """Load cache from disk."""
        try:
            with open(filepath, 'rb') as f:
                self.cache = pickle.load(f)
        except FileNotFoundError:
            pass

# Usage
fetcher = CachedDataFetcher(cache_hours=24)
df1, _ = fetcher.fetch('AAPL', '1y')  # Fetches
df2, _ = fetcher.fetch('AAPL', '1y')  # From cache
```

### Strategy 2: LRU Cache

Limit cache size:

```python
from functools import lru_cache
from hashlib import md5

class SmartDataFetcher:
    @lru_cache(maxsize=100)
    def fetch(self, symbol, period='1y'):
        """Cache last 100 unique fetches."""
        df, error = stock_data_service.fetch_historical_data(symbol, period)
        return df, error

# Usage - automatic LRU caching
fetcher = SmartDataFetcher()
df1, _ = fetcher.fetch('AAPL', '1y')  # Fetches
df2, _ = fetcher.fetch('AAPL', '1y')  # Cached
```

### Strategy 3: Redis Cache

Distributed caching:

```python
import redis
import pickle

class RedisDataFetcher:
    def __init__(self, redis_url='redis://localhost:6379/0', ttl=86400):
        self.redis = redis.from_url(redis_url)
        self.ttl = ttl  # Time to live in seconds
    
    def _cache_key(self, symbol, period):
        return f"stock_data:{symbol}:{period}"
    
    def fetch(self, symbol, period='1y'):
        key = self._cache_key(symbol, period)
        
        # Check Redis cache
        cached = self.redis.get(key)
        if cached:
            print(f"Redis cache hit: {key}")
            return pickle.loads(cached), None
        
        # Fetch fresh data
        print(f"Redis cache miss: {key}")
        df, error = stock_data_service.fetch_historical_data(symbol, period)
        
        if not error:
            # Store in Redis with TTL
            self.redis.setex(key, self.ttl, pickle.dumps(df))
        
        return df, error

# Usage
fetcher = RedisDataFetcher(ttl=86400)  # 24 hours
df, _ = fetcher.fetch('AAPL', '1y')
```

---

## Batch Processing

### Strategy 1: Sequential Batch

Process symbols one by one:

```python
def fetch_batch_sequential(symbols, period='1y'):
    """Fetch data sequentially with rate limiting."""
    results = {}
    errors = {}
    
    for symbol in symbols:
        df, error = stock_data_service.fetch_historical_data(symbol, period)
        
        if error:
            errors[symbol] = error
        else:
            results[symbol] = df
        
        time.sleep(1)  # Rate limiting
    
    return results, errors

# Usage
symbols = ['AAPL', 'GOOGL', 'MSFT']
data, errors = fetch_batch_sequential(symbols)
```

### Strategy 2: Parallel Batch

Process multiple symbols concurrently:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_single(symbol, period='1y'):
    """Fetch single symbol."""
    df, error = stock_data_service.fetch_historical_data(symbol, period)
    return symbol, df, error

def fetch_batch_parallel(symbols, period='1y', max_workers=5):
    """Fetch data in parallel."""
    results = {}
    errors = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_single, symbol, period): symbol
            for symbol in symbols
        }
        
        for future in as_completed(futures):
            symbol, df, error = future.result()
            
            if error:
                errors[symbol] = error
            else:
                results[symbol] = df
    
    return results, errors

# Usage - much faster for many symbols
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
data, errors = fetch_batch_parallel(symbols, max_workers=5)
```

### Strategy 3: Smart Batching

Batch with retries and error handling:

```python
class SmartBatchFetcher:
    def __init__(self, max_retries=3, retry_delay=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def fetch_with_retry(self, symbol, period='1y'):
        """Fetch with automatic retries."""
        for attempt in range(self.max_retries):
            df, error = stock_data_service.fetch_historical_data(symbol, period)
            
            if not error:
                return df, None
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return None, f"Failed after {self.max_retries} attempts: {error}"
    
    def fetch_batch(self, symbols, period='1y'):
        """Batch fetch with smart error handling."""
        results = {}
        errors = {}
        
        for symbol in symbols:
            df, error = self.fetch_with_retry(symbol, period)
            
            if error:
                errors[symbol] = error
            else:
                results[symbol] = df
            
            time.sleep(0.5)  # Rate limiting
        
        return results, errors

# Usage
fetcher = SmartBatchFetcher(max_retries=3)
data, errors = fetcher.fetch_batch(['AAPL', 'GOOGL', 'MSFT'])
```

---

## Error Handling Patterns

### Pattern 1: Fallback Chain

Try multiple sources:

```python
def fetch_with_fallback(symbol, period='1y'):
    """Try multiple strategies."""
    
    # Strategy 1: Full period
    df, error = stock_data_service.fetch_historical_data(symbol, period)
    if not error:
        return df, None
    
    # Strategy 2: Shorter period
    if period in ['5y', '10y']:
        df, error = stock_data_service.fetch_historical_data(symbol, '1y')
        if not error:
            return df, f"Used 1y instead of {period}"
    
    # Strategy 3: Default data
    return None, f"All strategies failed: {error}"
```

### Pattern 2: Circuit Breaker

Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == 'OPEN':
            if (datetime.now() - self.last_failure).seconds > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                return None, "Circuit breaker is OPEN"
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failures = 0
            
            return result
        
        except Exception as e:
            self.failures += 1
            self.last_failure = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
            
            return None, str(e)

# Usage
breaker = CircuitBreaker()
df, error = breaker.call(
    stock_data_service.fetch_historical_data,
    'AAPL',
    period='1y'
)
```

---

## Data Quality Checks

### Validation Framework

```python
class DataValidator:
    @staticmethod
    def validate_dataframe(df, symbol):
        """Comprehensive data validation."""
        issues = []
        
        # Check if empty
        if df is None or df.empty:
            issues.append("DataFrame is empty")
            return False, issues
        
        # Check required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Check for missing values
        if df.isnull().any().any():
            null_counts = df.isnull().sum()
            issues.append(f"Missing values: {null_counts[null_counts > 0].to_dict()}")
        
        # Check data integrity
        if (df['High'] < df['Low']).any():
            issues.append("High < Low detected")
        
        if (df['Close'] > df['High']).any() or (df['Close'] < df['Low']).any():
            issues.append("Close outside High-Low range")
        
        # Check for outliers
        returns = df['Close'].pct_change()
        extreme_returns = returns[(returns.abs() > 0.20)]
        if len(extreme_returns) > 0:
            issues.append(f"Extreme returns detected: {len(extreme_returns)} days > 20%")
        
        # Check minimum data points
        if len(df) < 20:
            issues.append(f"Insufficient data: only {len(df)} rows")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def clean_dataframe(df):
        """Clean and fix data issues."""
        df = df.copy()
        
        # Forward fill missing values
        df = df.fillna(method='ffill')
        
        # Remove rows where High < Low
        df = df[df['High'] >= df['Low']]
        
        # Ensure Close is within High-Low
        df.loc[df['Close'] > df['High'], 'Close'] = df['High']
        df.loc[df['Close'] < df['Low'], 'Close'] = df['Low']
        
        return df

# Usage
df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')

if not error:
    valid, issues = DataValidator.validate_dataframe(df, 'AAPL')
    
    if not valid:
        print(f"Data quality issues: {issues}")
        df = DataValidator.clean_dataframe(df)
        print("Data cleaned")
```

---

## Performance Optimization

### Technique 1: Data Sampling

```python
def fetch_optimized(symbol, period='1y', sample_rate=None):
    """Fetch and optionally downsample data."""
    df, error = stock_data_service.fetch_historical_data(symbol, period)
    
    if error or df is None:
        return df, error
    
    # Downsample if requested
    if sample_rate:
        df = df.resample(sample_rate).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
    
    return df, None

# Usage - reduce data size
df, _ = fetch_optimized('AAPL', period='10y', sample_rate='W')  # Weekly
```

### Technique 2: Columnar Storage

```python
import pyarrow.parquet as pq

def save_optimized(df, symbol):
    """Save in efficient format."""
    filename = f"data/{symbol}.parquet"
    df.to_parquet(filename, compression='snappy')

def load_optimized(symbol):
    """Load from optimized storage."""
    filename = f"data/{symbol}.parquet"
    return pd.read_parquet(filename)

# Usage - much faster than CSV
df, _ = stock_data_service.fetch_historical_data('AAPL', period='10y')
save_optimized(df, 'AAPL')
df_loaded = load_optimized('AAPL')  # Very fast
```

---

## Monitoring and Logging

### Logging Framework

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_fetching.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MonitoredFetcher:
    def fetch(self, symbol, period='1y'):
        """Fetch with logging."""
        logger.info(f"Fetching {symbol} ({period})")
        start_time = time.time()
        
        df, error = stock_data_service.fetch_historical_data(symbol, period)
        
        elapsed = time.time() - start_time
        
        if error:
            logger.error(f"Failed to fetch {symbol}: {error}")
        else:
            logger.info(f"Fetched {symbol}: {len(df)} rows in {elapsed:.2f}s")
        
        return df, error

# Usage
fetcher = MonitoredFetcher()
df, _ = fetcher.fetch('AAPL', '1y')
```

---

## Summary Checklist

When implementing data fetching:

- [ ] Choose appropriate loading strategy (lazy/eager/incremental)
- [ ] Implement caching with proper TTL
- [ ] Add rate limiting for API calls
- [ ] Handle errors gracefully with fallbacks
- [ ] Validate data quality
- [ ] Clean and normalize data
- [ ] Log operations for monitoring
- [ ] Use efficient storage formats
- [ ] Implement retries for transient failures
- [ ] Monitor performance metrics
- [ ] Document data sources and update frequencies

---

## Next Steps

- [Using Services](../how_to/03_using_services.md)
- [Financial Data Fetching](../how_to/04_financial_data_fetching.md)
- [Performance Optimization](06_performance_optimization.md)