# Using Services in Timber

This guide explains how to use Timber's modular persistence and data services.

---

## Overview

Timber provides specialized services instead of one monolithic persistence layer. Each service handles a specific domain:

- **Session Service** - Manage user sessions
- **Research Service** - Store research data
- **Notification Service** - Create notifications
- **Tracker Service** - Track user activities
- **Stock Data Service** - Fetch financial data

---

## Session Service

Manages user sessions (research sessions, portfolio sessions, etc.)

### Import

```python
from timber.common.services.persistence import session_service
```

### Create a Session

```python
from timber.common.services.persistence import session_service
import uuid

# Create a research session
session_id = session_service.create_session(
    user_id='user-123',
    session_type='research',  # Type identifier
    metadata={
        'symbol': 'AAPL',
        'analysis_type': 'fundamental',
        'started_from': 'dashboard'
    }
)

print(f"Created session: {session_id}")
```

### Get Session

```python
# Get by ID
session = session_service.get_session(session_id)

print(f"Session status: {session.status}")
print(f"Created at: {session.created_at}")
print(f"Metadata: {session.metadata}")
```

### Update Session

```python
# Update status and metadata
session_service.update_session(
    session_id=session_id,
    status='in_progress',
    metadata={
        'symbol': 'AAPL',
        'analysis_type': 'fundamental',
        'progress': 50
    }
)
```

### List User Sessions

```python
# Get all sessions for a user
sessions = session_service.get_user_sessions(
    user_id='user-123',
    session_type='research',  # Optional filter
    status='active',          # Optional filter
    limit=10
)

for session in sessions:
    print(f"{session.id}: {session.metadata.get('symbol')}")
```

### Complete Session

```python
# Mark session as completed
session_service.complete_session(
    session_id=session_id,
    result={'recommendation': 'Buy', 'confidence': 0.85}
)
```

### Delete Session

```python
# Soft delete (recommended)
session_service.delete_session(
    session_id=session_id,
    user_id='user-123'
)

# Hard delete (permanent)
session_service.delete_session(
    session_id=session_id,
    user_id='user-123',
    hard_delete=True
)
```

---

## Research Service

Stores research data and analysis results.

### Import

```python
from timber.common.services.persistence import research_service
```

### Save Research

```python
# Save research data
research_id = research_service.save_research(
    session_id=session_id,
    content={
        'company_info': {
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'market_cap': 2800000000000
        },
        'financial_metrics': {
            'pe_ratio': 28.5,
            'revenue_growth': 0.12,
            'profit_margin': 0.26
        },
        'analysis': 'Strong fundamentals with consistent growth...'
    },
    research_type='fundamental',
    metadata={
        'analyst': 'user-123',
        'confidence': 0.85,
        'sources': ['10-K', 'earnings_call']
    }
)

print(f"Saved research: {research_id}")
```

### Get Research

```python
# Get by ID
research = research_service.get_research(research_id)

print(f"Type: {research.research_type}")
print(f"Content: {research.content}")
```

### List Session Research

```python
# Get all research for a session
research_list = research_service.get_session_research(
    session_id=session_id,
    research_type='fundamental'  # Optional filter
)

for research in research_list:
    print(f"- {research.research_type}: {research.created_at}")
```

### Update Research

```python
# Update existing research
research_service.update_research(
    research_id=research_id,
    content={
        'company_info': {...},
        'financial_metrics': {...},
        'analysis': 'Updated analysis...',
        'recommendation': 'Buy'
    },
    metadata={
        'updated_reason': 'New earnings data',
        'confidence': 0.90
    }
)
```

### Search Research

```python
# Search by user and type
results = research_service.search_research(
    user_id='user-123',
    research_type='fundamental',
    start_date='2024-01-01',
    end_date='2024-12-31',
    limit=20
)
```

---

## Notification Service

Creates and manages user notifications.

### Import

```python
from timber.common.services.persistence import notification_service
```

### Create Notification

```python
# Create a simple notification
notification_id = notification_service.create_notification(
    user_id='user-123',
    notification_type='alert',
    title='Price Alert',
    message='AAPL reached your target price of $180',
    data={
        'symbol': 'AAPL',
        'price': 180.50,
        'target': 180.00
    },
    priority='high'
)

print(f"Created notification: {notification_id}")
```

### Create Session Notification

```python
# Link notification to a session
notification_service.create_session_notification(
    user_id='user-123',
    session_id=session_id,
    notification_type='research_complete',
    title='Research Complete',
    message='Your AAPL analysis is ready',
    data={
        'session_id': session_id,
        'symbol': 'AAPL',
        'result': 'Buy recommendation'
    }
)
```

### Get User Notifications

```python
# Get unread notifications
notifications = notification_service.get_user_notifications(
    user_id='user-123',
    unread_only=True,
    limit=10
)

for notif in notifications:
    print(f"{notif.title}: {notif.message}")
```

### Mark as Read

```python
# Mark notification as read
notification_service.mark_as_read(
    notification_id=notification_id,
    user_id='user-123'
)

# Mark all as read
notification_service.mark_all_as_read(user_id='user-123')
```

### Delete Notification

```python
notification_service.delete_notification(
    notification_id=notification_id,
    user_id='user-123'
)
```

---

## Tracker Service

Tracks user activities and events.

### Import

```python
from timber.common.services.persistence import tracker_service
```

### Track Event

```python
# Track a user action
tracker_service.track_event(
    user_id='user-123',
    event_type='stock_viewed',
    event_data={
        'symbol': 'AAPL',
        'source': 'search',
        'duration_seconds': 45
    },
    metadata={
        'page': 'dashboard',
        'device': 'desktop'
    }
)
```

### Track Session Event

```python
# Track session-specific event
tracker_service.track_session_event(
    user_id='user-123',
    session_id=session_id,
    event_type='research_step_completed',
    event_data={
        'step': 'fundamental_analysis',
        'duration_seconds': 120,
        'result': 'success'
    }
)
```

### Get User Activity

```python
# Get recent activity
activity = tracker_service.get_user_activity(
    user_id='user-123',
    event_type='stock_viewed',  # Optional filter
    start_date='2024-01-01',    # Optional
    limit=50
)

for event in activity:
    print(f"{event.event_type}: {event.event_data.get('symbol')}")
```

### Get Session Events

```python
# Get all events for a session
events = tracker_service.get_session_events(
    session_id=session_id
)

for event in events:
    print(f"- {event.event_type} at {event.created_at}")
```

### Analytics

```python
# Get event counts
stats = tracker_service.get_event_stats(
    user_id='user-123',
    start_date='2024-01-01',
    end_date='2024-12-31',
    group_by='event_type'
)

for event_type, count in stats.items():
    print(f"{event_type}: {count}")
```

---

## Stock Data Service

Fetches financial data from multiple sources.

### Import

```python
from timber.common import stock_data_service
```

### Historical Data

```python
# Fetch historical price data
df, error = stock_data_service.fetch_historical_data(
    symbol='AAPL',
    period='1y'  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
)

if error:
    print(f"Error: {error}")
else:
    print(f"Fetched {len(df)} rows")
    print(df.head())
```

### Date Range

```python
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

df, error = stock_data_service.fetch_historical_data(
    symbol='AAPL',
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)
```

### Company Information

```python
# Get company profile
info, error = stock_data_service.fetch_company_info('AAPL')

if not error:
    print(f"Name: {info.get('longName')}")
    print(f"Sector: {info.get('sector')}")
    print(f"Industry: {info.get('industry')}")
    print(f"Market Cap: {info.get('marketCap')}")
    print(f"Website: {info.get('website')}")
```

### Financial Statements

```python
# Get financial statements
income, balance, cashflow, error = stock_data_service.fetch_financials(
    symbol='AAPL',
    period='yearly'  # or 'quarterly'
)

if not error:
    print("Income Statement:")
    print(income.head())
    
    print("\nBalance Sheet:")
    print(balance.head())
    
    print("\nCash Flow:")
    print(cashflow.head())
```

### News

```python
# Get recent news
news, error = stock_data_service.fetch_news(
    symbol='AAPL',
    limit=10
)

if not error:
    for article in news:
        print(f"- {article['title']}")
        print(f"  Published: {article['published']}")
        print(f"  Source: {article['source']}")
        print(f"  URL: {article['url']}")
        print()
```

### Multiple Symbols

```python
# Fetch data for multiple stocks
symbols = ['AAPL', 'GOOGL', 'MSFT']

for symbol in symbols:
    df, error = stock_data_service.fetch_historical_data(
        symbol=symbol,
        period='1mo'
    )
    
    if not error:
        latest_price = df['Close'].iloc[-1]
        print(f"{symbol}: ${latest_price:.2f}")
```

---

## Complete Workflow Example

Putting it all together:

```python
from timber.common.services.persistence import (
    session_service,
    research_service,
    notification_service,
    tracker_service
)
from timber.common import stock_data_service

# 1. Create a research session
session_id = session_service.create_session(
    user_id='user-123',
    session_type='research',
    metadata={'symbol': 'AAPL', 'analysis_type': 'comprehensive'}
)

# 2. Track session start
tracker_service.track_session_event(
    user_id='user-123',
    session_id=session_id,
    event_type='session_started',
    event_data={'symbol': 'AAPL'}
)

# 3. Fetch company information
info, error = stock_data_service.fetch_company_info('AAPL')
if error:
    print(f"Error fetching info: {error}")
    exit()

# 4. Fetch historical data
df, error = stock_data_service.fetch_historical_data('AAPL', period='5y')
if error:
    print(f"Error fetching data: {error}")
    exit()

# 5. Track data fetching
tracker_service.track_session_event(
    user_id='user-123',
    session_id=session_id,
    event_type='data_fetched',
    event_data={'rows': len(df), 'period': '5y'}
)

# 6. Perform analysis (your logic here)
analysis_result = {
    'company_info': info,
    'price_data': {
        'latest': float(df['Close'].iloc[-1]),
        'avg_5y': float(df['Close'].mean()),
        'volatility': float(df['Close'].std())
    },
    'recommendation': 'Buy',
    'confidence': 0.85
}

# 7. Save research
research_id = research_service.save_research(
    session_id=session_id,
    content=analysis_result,
    research_type='comprehensive',
    metadata={'analyst': 'user-123', 'confidence': 0.85}
)

# 8. Update session
session_service.update_session(
    session_id=session_id,
    status='completed',
    metadata={
        'symbol': 'AAPL',
        'result': 'Buy',
        'research_id': research_id
    }
)

# 9. Create notification
notification_service.create_session_notification(
    user_id='user-123',
    session_id=session_id,
    notification_type='research_complete',
    title='Analysis Complete',
    message=f"Your AAPL analysis is ready: {analysis_result['recommendation']}",
    data={'research_id': research_id, 'symbol': 'AAPL'}
)

# 10. Track completion
tracker_service.track_session_event(
    user_id='user-123',
    session_id=session_id,
    event_type='session_completed',
    event_data={'result': 'Buy', 'confidence': 0.85}
)

print(f"✅ Complete workflow finished!")
print(f"Session ID: {session_id}")
print(f"Research ID: {research_id}")
```

---

## Error Handling

All services return tuples with data and error:

```python
# Pattern 1: Check error first
data, error = some_service.method()
if error:
    print(f"Error: {error}")
    return

# Use data
print(data)
```

```python
# Pattern 2: Try-except for service exceptions
from timber.common.services.exceptions import ServiceError

try:
    result = session_service.create_session(...)
    print(f"Created: {result}")
except ServiceError as e:
    print(f"Service error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Database Sessions

Services handle database sessions automatically, but you can use manual sessions:

```python
from timber.common.models.base import db_manager
from timber.common import get_model

# Manual session management
with db_manager.session_scope() as session:
    # Get model
    ResearchSession = get_model('StockResearchSession')
    
    # Query directly
    active_sessions = session.query(ResearchSession)\
        .filter_by(user_id='user-123', status='active')\
        .all()
    
    for sess in active_sessions:
        print(f"{sess.id}: {sess.metadata}")
```

---

## Service Configuration

### Custom Timeouts

```python
from timber.common.utils.config import config

# Configure API timeouts
config.API_REQUEST_TIMEOUT = 30  # seconds
```

### Custom Cache TTL

```python
# Configure cache time-to-live
config.CACHE_TTL_HOURS = 6  # hours
```

### Enable/Disable Features

```python
# In your .env file
CACHE_ENABLED=True
REDIS_ENABLED=False
ENABLE_ENCRYPTION=True
ENABLE_AUTO_VECTOR_INGESTION=True
```

---

## Best Practices

### 1. Always Check Errors

```python
# Good
data, error = service.method()
if error:
    handle_error(error)
    return

# Bad - ignoring errors
data, _ = service.method()
use(data)  # Might be None!
```

### 2. Use Context Managers

```python
# Good - automatic cleanup
with db_manager.session_scope() as session:
    # Work with session
    pass

# Bad - manual management
session = db_manager.get_session()
# Work with session
session.close()  # Might forget!
```

### 3. Provide Meaningful Metadata

```python
# Good - detailed metadata
session_service.create_session(
    user_id='user-123',
    session_type='research',
    metadata={
        'symbol': 'AAPL',
        'analysis_type': 'fundamental',
        'source': 'dashboard',
        'device': 'desktop'
    }
)

# Okay - minimal metadata
session_service.create_session(
    user_id='user-123',
    session_type='research',
    metadata={'symbol': 'AAPL'}
)
```

### 4. Clean Up Sessions

```python
# Complete or delete finished sessions
if analysis_done:
    session_service.complete_session(session_id)
else:
    session_service.delete_session(session_id, user_id)
```

### 5. Track Important Events

```python
# Track meaningful activities
tracker_service.track_event(
    user_id='user-123',
    event_type='high_value_action',
    event_data={...}
)

# Don't over-track trivial events
# Avoid: tracking every mouse click
```

---

## Testing Services

```python
import pytest
from timber.common import initialize_timber
from timber.common.services.persistence import session_service

@pytest.fixture(scope='module')
def setup_timber():
    initialize_timber(model_config_dirs=['./data/models'])

def test_session_service(setup_timber):
    # Create session
    session_id = session_service.create_session(
        user_id='test-user',
        session_type='test',
        metadata={'test': True}
    )
    
    assert session_id is not None
    
    # Get session
    session = session_service.get_session(session_id)
    assert session.user_id == 'test-user'
    assert session.metadata['test'] == True
    
    # Cleanup
    session_service.delete_session(session_id, 'test-user', hard_delete=True)
```

---

## Common Patterns

### Pattern: Research Pipeline

```python
def run_research_pipeline(user_id: str, symbol: str):
    # Create session
    session_id = session_service.create_session(
        user_id=user_id,
        session_type='research',
        metadata={'symbol': symbol}
    )
    
    try:
        # Fetch data
        df, error = stock_data_service.fetch_historical_data(symbol, period='5y')
        if error:
            raise ValueError(f"Data fetch failed: {error}")
        
        # Analyze (your logic)
        result = analyze_stock(df)
        
        # Save research
        research_id = research_service.save_research(
            session_id=session_id,
            content=result,
            research_type='pipeline'
        )
        
        # Complete
        session_service.complete_session(session_id, result={'success': True})
        return research_id
        
    except Exception as e:
        # Mark failed
        session_service.update_session(
            session_id=session_id,
            status='failed',
            metadata={'error': str(e)}
        )
        raise
```

### Pattern: User Activity Summary

```python
def get_user_summary(user_id: str):
    # Get sessions
    sessions = session_service.get_user_sessions(
        user_id=user_id,
        limit=100
    )
    
    # Get activity
    activity = tracker_service.get_user_activity(
        user_id=user_id,
        limit=500
    )
    
    # Get notifications
    notifications = notification_service.get_user_notifications(
        user_id=user_id,
        unread_only=True
    )
    
    return {
        'total_sessions': len(sessions),
        'active_sessions': sum(1 for s in sessions if s.status == 'active'),
        'total_activities': len(activity),
        'unread_notifications': len(notifications)
    }
```

---

## Troubleshooting

### Issue: "Service returned None"

**Cause:** Database not initialized or model not found

**Solution:**
```python
from timber.common import initialize_timber

initialize_timber(model_config_dirs=['./data/models'])
```

### Issue: "Session not found"

**Cause:** Session deleted or invalid ID

**Solution:** Check if session exists first
```python
session = session_service.get_session(session_id)
if session is None:
    print("Session not found")
```

### Issue: "Data fetch timeout"

**Cause:** API timeout too short

**Solution:** Increase timeout
```python
from timber.common.utils.config import config
config.API_REQUEST_TIMEOUT = 60
```

---

## Next Steps

- [Financial Data Fetching](04_financial_data_fetching.md) - Deep dive into stock data
- [Testing Guide](08_testing_guide.md) - Testing services
- [Best Practices: Service Architecture](../best_practices/02_service_architecture.md)
- [Design Guide: Persistence Layer](../design_guides/03_persistence_layer.md)

---

## Summary

You've learned how to:
- ✅ Use session service for session management
- ✅ Save research data with research service
- ✅ Create notifications for users
- ✅ Track user activities and events
- ✅ Fetch stock data from multiple sources
- ✅ Build complete workflows
- ✅ Handle errors properly
- ✅ Follow best practices