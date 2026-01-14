# Error Handling Best Practices

**Comprehensive guide to robust error handling in Timber**

---

## Table of Contents

1. [Overview](#overview)
2. [Error Handling Principles](#error-handling-principles)
3. [Exception Hierarchy](#exception-hierarchy)
4. [Handling Patterns](#handling-patterns)
5. [Logging and Monitoring](#logging-and-monitoring)
6. [Recovery Strategies](#recovery-strategies)
7. [Common Patterns](#common-patterns)
8. [Anti-Patterns](#anti-patterns)

---

## Overview

Proper error handling is critical for building reliable, maintainable applications. Timber follows structured error handling practices across all services.

### Error Handling Goals

✅ **Fail Gracefully**: Don't crash, degrade gracefully  
✅ **Informative**: Clear error messages for debugging  
✅ **Actionable**: Users know what to do  
✅ **Logged**: All errors captured for analysis  
✅ **Recovered**: Automatic recovery when possible

---

## Error Handling Principles

### 1. Be Specific with Exceptions

**✅ GOOD**:
```python
class SessionNotFoundError(Exception):
    """Raised when session cannot be found."""
    pass

class InvalidSessionTypeError(ValueError):
    """Raised when session type is invalid."""
    pass

def get_session(session_id, session_type):
    if session_type not in VALID_TYPES:
        raise InvalidSessionTypeError(f"Invalid type: {session_type}")
    
    session = db.query(Session).get(session_id)
    if not session:
        raise SessionNotFoundError(f"Session {session_id} not found")
    
    return session
```

**❌ BAD**:
```python
def get_session(session_id, session_type):
    if session_type not in VALID_TYPES:
        raise Exception("Invalid")  # Too vague!
    
    session = db.query(Session).get(session_id)
    if not session:
        raise Exception("Not found")  # What wasn't found?
    
    return session
```

### 2. Return Errors, Don't Hide Them

**✅ GOOD**:
```python
def fetch_stock_data(symbol):
    """
    Fetch stock data.
    
    Returns:
        Tuple[Optional[DataFrame], Optional[str]]: (data, error)
    """
    try:
        df = yf.download(symbol, period='1y')
        if df.empty:
            return None, f"No data found for {symbol}"
        return df, None
    except Exception as e:
        logger.error(f"Failed to fetch {symbol}: {e}")
        return None, str(e)

# Caller handles error
data, error = fetch_stock_data('AAPL')
if error:
    print(f"Error: {error}")
else:
    process(data)
```

**❌ BAD**:
```python
def fetch_stock_data(symbol):
    try:
        df = yf.download(symbol, period='1y')
        return df
    except Exception as e:
        logger.error(f"Error: {e}")
        return pd.DataFrame()  # Empty DataFrame - error hidden!

# Caller doesn't know if empty = error or no data
data = fetch_stock_data('AAPL')
if data.empty:
    # Was it an error? Or just no data?
    pass
```

### 3. Handle Errors at the Right Level

```python
# Low-level: Raise exceptions
def fetch_from_api(url):
    """Raise exception on error."""
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError
    return response.json()

# Mid-level: Convert to domain errors
def get_company_data(symbol):
    """Return (data, error) tuple."""
    try:
        url = f"https://api.example.com/company/{symbol}"
        return fetch_from_api(url), None
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None, f"Company {symbol} not found"
        return None, f"API error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

# High-level: Handle errors for user
@app.route('/company/<symbol>')
def company_endpoint(symbol):
    """Handle errors at API boundary."""
    data, error = get_company_data(symbol)
    
    if error:
        if "not found" in error:
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 500
    
    return jsonify(data), 200
```

---

## Exception Hierarchy

### Custom Exception Classes

```python
# Base exception
class TimberError(Exception):
    """Base exception for all Timber errors."""
    pass

# Category exceptions
class DataFetchError(TimberError):
    """Error fetching data from external source."""
    pass

class CacheError(TimberError):
    """Error with caching operations."""
    pass

class ValidationError(TimberError):
    """Error validating data."""
    pass

# Specific exceptions
class SymbolNotFoundError(DataFetchError):
    """Stock symbol not found."""
    
    def __init__(self, symbol):
        self.symbol = symbol
        super().__init__(f"Symbol not found: {symbol}")

class APIRateLimitError(DataFetchError):
    """API rate limit exceeded."""
    
    def __init__(self, retry_after=None):
        self.retry_after = retry_after
        msg = "API rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"
        super().__init__(msg)

# Usage
try:
    data = fetch_stock_data('INVALID')
except SymbolNotFoundError as e:
    print(f"Symbol error: {e.symbol}")
except APIRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except DataFetchError as e:
    print(f"Data fetch failed: {e}")
```

---

## Handling Patterns

### Pattern 1: Retry with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_attempts=3, base_delay=1, max_delay=60, 
                       backoff_factor=2, exceptions=(Exception,)):
    """Retry decorator with exponential backoff."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            delay = base_delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            return None
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_attempts=3, exceptions=(requests.RequestException,))
def fetch_data_from_api(url):
    """Fetch with automatic retry."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Pattern 2: Circuit Breaker

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, failure_threshold=5, timeout_seconds=60, 
                 success_threshold=2):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: OPEN -> HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker: CLOSED -> OPEN")

# Usage
breaker = CircuitBreaker(failure_threshold=5)

def fetch_data(symbol):
    return breaker.call(external_api.fetch, symbol)
```

### Pattern 3: Fallback Chain

```python
class DataFetcherWithFallback:
    """Data fetcher with fallback sources."""
    
    def __init__(self):
        self.sources = [
            ('yfinance', self._fetch_yfinance),
            ('alphavantage', self._fetch_alphavantage),
            ('polygon', self._fetch_polygon),
            ('cache', self._fetch_from_cache),
        ]
    
    def fetch_data(self, symbol):
        """Fetch with fallback chain."""
        errors = []
        
        for source_name, fetch_func in self.sources:
            try:
                logger.info(f"Trying {source_name} for {symbol}")
                data = fetch_func(symbol)
                
                if data is not None:
                    logger.info(f"Success with {source_name}")
                    return data, None
                    
            except Exception as e:
                error_msg = f"{source_name} failed: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # All sources failed
        error = "All sources failed: " + "; ".join(errors)
        logger.error(error)
        return None, error
```

### Pattern 4: Timeout Protection

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import signal

def timeout_handler(func, args=(), kwargs={}, timeout=30):
    """Execute function with timeout."""
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logger.error(f"Function {func.__name__} timed out after {timeout}s")
            raise TimeoutError(f"Operation timed out after {timeout} seconds")

# Usage
try:
    result = timeout_handler(slow_function, args=('param',), timeout=10)
except TimeoutError:
    print("Operation timed out")
```

---

## Logging and Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Logger with structured output."""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log_error(self, error, context=None):
        """Log error with context."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'ERROR',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.logger.error(json.dumps(log_entry))
    
    def log_operation(self, operation, success, duration=None, metadata=None):
        """Log operation result."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'success': success,
            'duration_ms': duration,
            'metadata': metadata or {}
        }
        
        level = 'INFO' if success else 'ERROR'
        self.logger.log(getattr(logging, level), json.dumps(log_entry))

# Usage
logger = StructuredLogger('timber.services')

try:
    start = time.time()
    result = fetch_data('AAPL')
    duration = (time.time() - start) * 1000
    
    logger.log_operation(
        operation='fetch_data',
        success=True,
        duration=duration,
        metadata={'symbol': 'AAPL', 'rows': len(result)}
    )
except Exception as e:
    logger.log_error(e, context={'symbol': 'AAPL'})
```

### Error Tracking

```python
class ErrorTracker:
    """Track errors for monitoring and alerting."""
    
    def __init__(self):
        self.errors = defaultdict(list)
        self.error_counts = Counter()
    
    def record_error(self, error_type, error_message, context=None):
        """Record an error."""
        error_data = {
            'timestamp': datetime.utcnow(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        
        self.errors[error_type].append(error_data)
        self.error_counts[error_type] += 1
    
    def get_error_rate(self, error_type, window_minutes=60):
        """Get error rate for type in time window."""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        recent_errors = [
            e for e in self.errors[error_type]
            if e['timestamp'] > cutoff
        ]
        
        return len(recent_errors) / window_minutes  # per minute
    
    def should_alert(self, error_type, threshold=10):
        """Check if error rate exceeds threshold."""
        rate = self.get_error_rate(error_type)
        return rate > threshold

# Usage
tracker = ErrorTracker()

try:
    fetch_data('AAPL')
except DataFetchError as e:
    tracker.record_error('DataFetchError', str(e), {'symbol': 'AAPL'})
    
    if tracker.should_alert('DataFetchError'):
        send_alert("High error rate for DataFetchError")
```

---

## Recovery Strategies

### Strategy 1: Automatic Retry

```python
def with_retry(func):
    """Decorator for automatic retry."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == 2:
                    raise
                logger.warning(f"Retry {attempt + 1}/3: {e}")
                time.sleep(2 ** attempt)
    return wrapper
```

### Strategy 2: Graceful Degradation

```python
class DataService:
    """Service with graceful degradation."""
    
    def get_company_data(self, symbol):
        """Get data with degradation."""
        try:
            # Try full data
            return self._fetch_full_data(symbol)
        except Exception:
            logger.warning("Full data unavailable, trying basic data")
            
            try:
                # Fallback to basic data
                return self._fetch_basic_data(symbol)
            except Exception:
                logger.warning("Basic data unavailable, using cached")
                
                # Last resort: cached data
                return self._get_cached_data(symbol) or {'symbol': symbol}
```

### Strategy 3: Dead Letter Queue

```python
class DeadLetterQueue:
    """Queue for failed operations."""
    
    def __init__(self):
        self.failed_operations = []
    
    def add_failed(self, operation, error, context):
        """Add failed operation to queue."""
        self.failed_operations.append({
            'operation': operation,
            'error': str(error),
            'context': context,
            'timestamp': datetime.utcnow(),
            'retry_count': 0
        })
    
    def retry_failed(self):
        """Retry failed operations."""
        for op in self.failed_operations[:]:
            try:
                # Retry operation
                result = op['operation'](**op['context'])
                
                # Success - remove from queue
                self.failed_operations.remove(op)
                logger.info(f"Successfully retried: {op}")
                
            except Exception as e:
                op['retry_count'] += 1
                
                if op['retry_count'] >= 3:
                    logger.error(f"Failed after 3 retries: {op}")
                    self.failed_operations.remove(op)
```

---

## Common Patterns

### Pattern: Context Manager for Error Handling

```python
from contextlib import contextmanager

@contextmanager
def error_handler(operation_name, reraise=True):
    """Context manager for consistent error handling."""
    start_time = time.time()
    
    try:
        yield
        
        duration = time.time() - start_time
        logger.info(f"{operation_name} completed in {duration:.2f}s")
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"{operation_name} failed after {duration:.2f}s: {e}")
        
        # Track error
        error_tracker.record_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={'operation': operation_name, 'duration': duration}
        )
        
        if reraise:
            raise

# Usage
with error_handler('fetch_stock_data'):
    data = fetch_stock_data('AAPL')
    process_data(data)
```

---

## Anti-Patterns

### 1. Swallowing Exceptions

**❌ BAD**:
```python
try:
    critical_operation()
except:
    pass  # Silent failure!
```

### 2. Generic Exception Catching

**❌ BAD**:
```python
try:
    operation()
except Exception:  # Too broad!
    pass
```

### 3. Not Logging Errors

**❌ BAD**:
```python
try:
    operation()
except SpecificError:
    return None  # Error not logged!
```

---

## Summary

### Key Takeaways

1. **Be Specific**: Use specific exception types
2. **Return Errors**: Don't hide errors from callers
3. **Log Everything**: Comprehensive logging for debugging
4. **Retry Smart**: Exponential backoff for transient failures
5. **Degrade Gracefully**: Fallback to cached/basic data
6. **Monitor**: Track error rates and alert on thresholds

### Error Handling Checklist

- [ ] Specific exception types defined
- [ ] Errors logged with context
- [ ] Return (result, error) tuples
- [ ] Retry logic for transient failures
- [ ] Circuit breaker for external services
- [ ] Fallback mechanisms in place
- [ ] Error monitoring and alerting
- [ ] Documentation of error scenarios

---

**Last Updated**: October 19, 2024  
**Version**: 0.2.0