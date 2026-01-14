# Financial Data Fetching with Timber

Comprehensive guide to fetching stock data from multiple sources using Timber's unified API.

---

## Overview

Timber provides a unified interface to fetch financial data from multiple sources:
- **yfinance** (free, primary source)
- **Alpha Vantage** (free tier available)
- **Polygon.io** (premium)
- **Finnhub** (premium)

The `stock_data_service` automatically selects the best available source based on your environment and API key configuration.

---

## Quick Start

```python
from timber.common import stock_data_service

# Fetch historical data
df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')

if error:
    print(f"Error: {error}")
else:
    print(f"Fetched {len(df)} rows")
    print(df.head())
```

---

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Primary source (free, no key needed)
# yfinance is used by default

# Optional: Alpha Vantage (free tier: 5 calls/min, 500 calls/day)
ALPHA_VANTAGE_API_KEY=your_key_here

# Optional: Polygon (premium)
POLYGON_API_KEY=your_key_here

# Optional: Finnhub (free tier: 60 calls/min)
FINNHUB_API_KEY=your_key_here

# Optional: FRED (Federal Reserve Economic Data)
FRED_API_KEY=your_key_here

# Environment selection
OAK_ENV=development  # development uses free sources
# OAK_ENV=production  # production prefers premium sources

# Request timeout
API_REQUEST_TIMEOUT=30
```

### Check Configuration

```python
from timber.common.utils.config import config

# Check which APIs are configured
api_status = config.validate_api_keys()

for service, is_configured in api_status.items():
    status = "✓" if is_configured else "✗"
    print(f"{status} {service}")
```

---

## Historical Price Data

### By Period

```python
# Predefined periods
periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

for period in ['1mo', '1y', '5y']:
    df, error = stock_data_service.fetch_historical_data('AAPL', period=period)
    
    if not error:
        print(f"{period}: {len(df)} rows, from {df.index[0]} to {df.index[-1]}")
```

### By Date Range

```python
from datetime import datetime, timedelta

# Last 365 days
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

df, error = stock_data_service.fetch_historical_data(
    symbol='AAPL',
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

if not error:
    print(f"Fetched {len(df)} rows")
    print(df.head())
```

### Data Structure

The returned DataFrame has these columns:

```python
# Standard OHLCV format
columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Example usage
df, error = stock_data_service.fetch_historical_data('AAPL', period='1mo')

if not error:
    print(f"Latest close: ${df['Close'].iloc[-1]:.2f}")
    print(f"Average volume: {df['Volume'].mean():,.0f}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
```

### Intervals

```python
# Default: daily data
df, error = stock_data_service.fetch_historical_data(
    symbol='AAPL',
    period='1mo',
    interval='1d'  # Options: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
)
```

---

## Company Information

### Basic Information

```python
info, error = stock_data_service.fetch_company_info('AAPL')

if not error:
    print(f"Company: {info.get('longName')}")
    print(f"Sector: {info.get('sector')}")
    print(f"Industry: {info.get('industry')}")
    print(f"Website: {info.get('website')}")
    print(f"Employees: {info.get('fullTimeEmployees'):,}")
    print(f"Description: {info.get('longBusinessSummary', '')[:200]}...")
```

### Valuation Metrics

```python
info, error = stock_data_service.fetch_company_info('AAPL')

if not error:
    metrics = {
        'Market Cap': info.get('marketCap'),
        'Enterprise Value': info.get('enterpriseValue'),
        'P/E Ratio': info.get('trailingPE'),
        'Forward P/E': info.get('forwardPE'),
        'PEG Ratio': info.get('pegRatio'),
        'Price to Book': info.get('priceToBook'),
        'Price to Sales': info.get('priceToSalesTrailing12Months')
    }
    
    for metric, value in metrics.items():
        if value:
            print(f"{metric}: {value:,.2f}" if isinstance(value, (int, float)) else f"{metric}: {value}")
```

### Financial Ratios

```python
info, error = stock_data_service.fetch_company_info('AAPL')

if not error:
    ratios = {
        'Profit Margin': info.get('profitMargins'),
        'Operating Margin': info.get('operatingMargins'),
        'Return on Assets': info.get('returnOnAssets'),
        'Return on Equity': info.get('returnOnEquity'),
        'Revenue Growth': info.get('revenueGrowth'),
        'Earnings Growth': info.get('earningsGrowth'),
        'Debt to Equity': info.get('debtToEquity'),
        'Current Ratio': info.get('currentRatio'),
        'Quick Ratio': info.get('quickRatio')
    }
    
    for ratio, value in ratios.items():
        if value:
            print(f"{ratio}: {value:.2%}" if ratio.endswith(('Margin', 'Growth')) else f"{ratio}: {value:.2f}")
```

---

## Financial Statements

### Income Statement

```python
income, balance, cashflow, error = stock_data_service.fetch_financials(
    symbol='AAPL',
    period='yearly'  # or 'quarterly'
)

if not error:
    print("Income Statement:")
    print(income[['Total Revenue', 'Net Income', 'Gross Profit']].head())
    
    # Calculate metrics
    latest = income.iloc[0]
    revenue = latest['Total Revenue']
    net_income = latest['Net Income']
    profit_margin = (net_income / revenue) * 100
    
    print(f"\nLatest Year:")
    print(f"Revenue: ${revenue:,.0f}")
    print(f"Net Income: ${net_income:,.0f}")
    print(f"Profit Margin: {profit_margin:.2f}%")
```

### Balance Sheet

```python
income, balance, cashflow, error = stock_data_service.fetch_financials(
    symbol='AAPL',
    period='yearly'
)

if not error:
    print("Balance Sheet:")
    print(balance[['Total Assets', 'Total Liabilities', 'Stockholders Equity']].head())
    
    # Calculate ratios
    latest = balance.iloc[0]
    assets = latest['Total Assets']
    liabilities = latest['Total Liabilities']
    equity = latest['Stockholders Equity']
    
    debt_to_equity = liabilities / equity
    
    print(f"\nLatest Year:")
    print(f"Total Assets: ${assets:,.0f}")
    print(f"Total Liabilities: ${liabilities:,.0f}")
    print(f"Equity: ${equity:,.0f}")
    print(f"Debt to Equity: {debt_to_equity:.2f}")
```

### Cash Flow Statement

```python
income, balance, cashflow, error = stock_data_service.fetch_financials(
    symbol='AAPL',
    period='yearly'
)

if not error:
    print("Cash Flow Statement:")
    print(cashflow[['Operating Cash Flow', 'Free Cash Flow', 'Capital Expenditure']].head())
    
    # Calculate free cash flow
    latest = cashflow.iloc[0]
    operating_cf = latest['Operating Cash Flow']
    capex = latest['Capital Expenditure']
    free_cf = operating_cf + capex  # capex is negative
    
    print(f"\nLatest Year:")
    print(f"Operating Cash Flow: ${operating_cf:,.0f}")
    print(f"Capital Expenditure: ${capex:,.0f}")
    print(f"Free Cash Flow: ${free_cf:,.0f}")
```

### Quarterly Financials

```python
# Get quarterly data for trend analysis
income_q, balance_q, cashflow_q, error = stock_data_service.fetch_financials(
    symbol='AAPL',
    period='quarterly'
)

if not error:
    # Plot revenue trend
    import matplotlib.pyplot as plt
    
    quarters = income_q.index[:8]  # Last 8 quarters
    revenues = income_q['Total Revenue'][:8]
    
    plt.figure(figsize=(10, 6))
    plt.plot(quarters, revenues, marker='o')
    plt.title('AAPL Quarterly Revenue Trend')
    plt.xlabel('Quarter')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
```

---

## News and Sentiment

### Recent News

```python
news, error = stock_data_service.fetch_news('AAPL', limit=10)

if not error:
    print(f"Found {len(news)} news articles\n")
    
    for i, article in enumerate(news, 1):
        print(f"{i}. {article['title']}")
        print(f"   Published: {article['published']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url']}")
        print()
```

### News with Date Filter

```python
from datetime import datetime, timedelta

# News from last 7 days
start_date = datetime.now() - timedelta(days=7)

news, error = stock_data_service.fetch_news(
    symbol='AAPL',
    start_date=start_date.strftime('%Y-%m-%d'),
    limit=20
)

if not error:
    print(f"News from last 7 days: {len(news)} articles")
```

### News Analysis

```python
# Analyze news sentiment (requires additional libraries)
news, error = stock_data_service.fetch_news('AAPL', limit=50)

if not error:
    # Count sources
    sources = {}
    for article in news:
        source = article['source']
        sources[source] = sources.get(source, 0) + 1
    
    print("News by Source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}")
    
    # Keywords analysis
    keywords = {}
    for article in news:
        title = article['title'].lower()
        for word in title.split():
            if len(word) > 4:
                keywords[word] = keywords.get(word, 0) + 1
    
    print("\nTop Keywords:")
    for word, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {word}: {count}")
```

---

## Multiple Symbols

### Batch Fetching

```python
# Fetch data for multiple stocks
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']

results = {}
for symbol in symbols:
    df, error = stock_data_service.fetch_historical_data(symbol, period='1mo')
    
    if not error:
        results[symbol] = {
            'data': df,
            'latest_price': df['Close'].iloc[-1],
            'month_return': (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        }

# Display results
print("Symbol | Latest Price | 1-Month Return")
print("-" * 45)
for symbol, data in results.items():
    print(f"{symbol:6} | ${data['latest_price']:12.2f} | {data['month_return']:+.2f}%")
```

### Portfolio Analysis

```python
# Analyze a portfolio
portfolio = {
    'AAPL': 100,   # 100 shares
    'GOOGL': 50,
    'MSFT': 75,
    'AMZN': 25
}

total_value = 0
portfolio_data = {}

for symbol, shares in portfolio.items():
    df, error = stock_data_service.fetch_historical_data(symbol, period='1d')
    
    if not error:
        price = df['Close'].iloc[-1]
        value = price * shares
        total_value += value
        
        portfolio_data[symbol] = {
            'shares': shares,
            'price': price,
            'value': value
        }

# Display portfolio
print("Portfolio Summary")
print("=" * 50)
for symbol, data in portfolio_data.items():
    weight = (data['value'] / total_value) * 100
    print(f"{symbol}: {data['shares']} shares @ ${data['price']:.2f} = ${data['value']:,.2f} ({weight:.1f}%)")

print(f"\nTotal Portfolio Value: ${total_value:,.2f}")
```

---

## Advanced Analysis

### Technical Indicators

```python
import pandas as pd

def add_technical_indicators(df):
    """Add common technical indicators to price data."""
    
    # Moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # Exponential moving average
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    
    return df

# Use it
df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')

if not error:
    df = add_technical_indicators(df)
    
    # Check signals
    latest = df.iloc[-1]
    print(f"Latest Close: ${latest['Close']:.2f}")
    print(f"SMA 20: ${latest['SMA_20']:.2f}")
    print(f"SMA 50: ${latest['SMA_50']:.2f}")
    print(f"RSI: {latest['RSI']:.2f}")
    print(f"MACD: {latest['MACD']:.2f}")
    
    # Trading signals
    if latest['Close'] > latest['SMA_50']:
        print("✓ Price above 50-day MA (Bullish)")
    
    if latest['RSI'] > 70:
        print("⚠ RSI > 70 (Overbought)")
    elif latest['RSI'] < 30:
        print("⚠ RSI < 30 (Oversold)")
```

### Returns Analysis

```python
def calculate_returns(df):
    """Calculate various return metrics."""
    
    # Daily returns
    df['Daily_Return'] = df['Close'].pct_change()
    
    # Cumulative returns
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
    
    # Log returns
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    
    return df

df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')

if not error:
    df = calculate_returns(df)
    
    # Statistics
    total_return = df['Cumulative_Return'].iloc[-1]
    avg_daily_return = df['Daily_Return'].mean()
    volatility = df['Daily_Return'].std()
    sharpe_ratio = (avg_daily_return / volatility) * (252 ** 0.5)  # Annualized
    
    print(f"1-Year Performance:")
    print(f"Total Return: {total_return:.2%}")
    print(f"Avg Daily Return: {avg_daily_return:.4%}")
    print(f"Volatility (daily): {volatility:.4%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    
    # Max drawdown
    cummax = df['Close'].cummax()
    drawdown = (df['Close'] - cummax) / cummax
    max_drawdown = drawdown.min()
    print(f"Max Drawdown: {max_drawdown:.2%}")
```

### Correlation Analysis

```python
# Analyze correlation between stocks
symbols = ['AAPL', 'MSFT', 'GOOGL']

# Fetch data
data = {}
for symbol in symbols:
    df, error = stock_data_service.fetch_historical_data(symbol, period='1y')
    if not error:
        data[symbol] = df['Close']

# Create DataFrame
prices = pd.DataFrame(data)

# Calculate returns
returns = prices.pct_change().dropna()

# Correlation matrix
correlation = returns.corr()
print("Correlation Matrix:")
print(correlation)

# Visualize
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
plt.title('Stock Returns Correlation')
plt.show()
```

---

## Real-Time Data

### Latest Quote

```python
# Get most recent price
df, error = stock_data_service.fetch_historical_data('AAPL', period='1d')

if not error:
    latest = df.iloc[-1]
    
    print(f"Symbol: AAPL")
    print(f"Latest Price: ${latest['Close']:.2f}")
    print(f"Open: ${latest['Open']:.2f}")
    print(f"High: ${latest['High']:.2f}")
    print(f"Low: ${latest['Low']:.2f}")
    print(f"Volume: {latest['Volume']:,.0f}")
    print(f"Date: {latest.name.strftime('%Y-%m-%d %H:%M:%S')}")
```

### Price Change

```python
df, error = stock_data_service.fetch_historical_data('AAPL', period='5d')

if not error:
    latest = df['Close'].iloc[-1]
    previous = df['Close'].iloc[-2]
    
    change = latest - previous
    change_pct = (change / previous) * 100
    
    direction = "↑" if change > 0 else "↓"
    print(f"AAPL: ${latest:.2f} {direction} ${abs(change):.2f} ({change_pct:+.2f}%)")
```

---

## Error Handling and Fallbacks

### Graceful Degradation

```python
def fetch_with_fallback(symbol, period='1y'):
    """Fetch data with fallback strategy."""
    
    # Try primary source
    df, error = stock_data_service.fetch_historical_data(symbol, period=period)
    
    if error:
        print(f"Primary source failed: {error}")
        
        # Try alternative period
        if period == '5y':
            print("Trying 1y period...")
            df, error = stock_data_service.fetch_historical_data(symbol, period='1y')
        
        if error:
            print("All attempts failed")
            return None, error
    
    return df, None

# Use it
df, error = fetch_with_fallback('AAPL', period='5y')
if df is not None:
    print(f"Successfully fetched {len(df)} rows")
```

### Retry Logic

```python
import time

def fetch_with_retry(symbol, max_retries=3, delay=5):
    """Fetch data with retry logic."""
    
    for attempt in range(max_retries):
        df, error = stock_data_service.fetch_historical_data(symbol, period='1y')
        
        if not error:
            return df, None
        
        if attempt < max_retries - 1:
            print(f"Attempt {attempt + 1} failed: {error}")
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return None, f"Failed after {max_retries} attempts"

# Use it
df, error = fetch_with_retry('AAPL')
if df is not None:
    print("Success!")
```

---

## Caching

### Built-in Caching

```python
# Timber automatically caches responses
# First call: fetches from API
df1, error = stock_data_service.fetch_historical_data('AAPL', period='1y')

# Second call: returns from cache (much faster)
df2, error = stock_data_service.fetch_historical_data('AAPL', period='1y')
```

### Cache Control

```python
from timber.common.utils.config import config

# Configure cache TTL
config.CACHE_TTL_HOURS = 6  # Cache for 6 hours

# Enable/disable cache
config.CACHE_ENABLED = True
```

---

## Best Practices

### 1. Check for Errors

```python
# Always check errors
df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')
if error:
    print(f"Error: {error}")
    return

# Proceed with data
analyze(df)
```

### 2. Validate Symbols

```python
from timber.common.utils.validators import validate_stock_symbol

symbol = user_input.upper().strip()

if not validate_stock_symbol(symbol):
    print(f"Invalid symbol: {symbol}")
    return

df, error = stock_data_service.fetch_historical_data(symbol, period='1y')
```

### 3. Handle Missing Data

```python
df, error = stock_data_service.fetch_historical_data('AAPL', period='5y')

if not error:
    # Check for missing values
    if df.isnull().any().any():
        print("Warning: Missing data detected")
        df = df.fillna(method='ffill')  # Forward fill
    
    # Check data quality
    if len(df) < 252:  # Less than 1 year of trading days
        print("Warning: Insufficient data")
```

### 4. Rate Limiting

```python
import time

symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']

for symbol in symbols:
    df, error = stock_data_service.fetch_historical_data(symbol, period='1y')
    
    if not error:
        print(f"Fetched {symbol}")
    
    # Respect API rate limits
    time.sleep(1)  # 1 second between requests
```

### 5. Save Data Locally

```python
# Save for later use
df, error = stock_data_service.fetch_historical_data('AAPL', period='5y')

if not error:
    # Save to CSV
    df.to_csv('aapl_5y.csv')
    
    # Save to parquet (more efficient)
    df.to_parquet('aapl_5y.parquet')
    
    # Load later
    df_loaded = pd.read_parquet('aapl_5y.parquet')
```

---

## Troubleshooting

### Issue: API Key Not Found

**Solution:** Check your `.env` file
```bash
cat .env | grep API_KEY
```

### Issue: Rate Limit Exceeded

**Solution:** Add delays or use cache
```python
import time
time.sleep(12)  # Wait before next request
```

### Issue: Symbol Not Found

**Solution:** Validate symbol first
```python
from timber.common.utils.validators import validate_stock_symbol

if not validate_stock_symbol(symbol):
    print("Invalid symbol")
```

### Issue: Empty DataFrame

**Solution:** Check date range and symbol
```python
df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')

if df.empty:
    print("No data returned - check symbol and date range")
```

---

## Next Steps

- [Using Services](03_using_services.md) - Integrate with persistence
- [Best Practices: Data Fetching](../best_practices/03_data_fetching_strategies.md)
- [Testing Guide](08_testing_guide.md) - Test data fetching

---

## Summary

You've learned how to:
- ✅ Configure API keys for multiple sources
- ✅ Fetch historical price data
- ✅ Get company information and metrics
- ✅ Retrieve financial statements
- ✅ Access news and sentiment
- ✅ Analyze multiple symbols
- ✅ Calculate technical indicators
- ✅ Perform returns and correlation analysis
- ✅ Handle errors and implement fallbacks
- ✅ Use caching effectively
- ✅ Follow best practices