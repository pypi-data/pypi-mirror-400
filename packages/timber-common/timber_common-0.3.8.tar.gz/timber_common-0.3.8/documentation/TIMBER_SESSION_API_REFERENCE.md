# Timber Session Service API - Quick Reference

## 📚 Correct API Usage

### create_session()

```python
session_id = timber_session_service.create_session(
    user_id='user-123',           # Required, keyword arg
    session_type='stock_research', # Required, keyword arg (workflow name!)
    metadata={...}                 # Required, keyword arg
)
```

**Key Points:**
- ✅ All keyword arguments
- ✅ `session_type` = workflow name (not model name)
- ✅ Returns: session_id (str)

---

### get_session()

```python
session = timber_session_service.get_session(
    session_id='abc-123',         # Required, keyword arg
    session_type='stock_research'  # Required, keyword arg
)
```

**Key Points:**
- ✅ Requires `session_type` parameter
- ✅ Returns: session dict or None
- ⚠️  Must know the session_type in advance

**Solution for unknown session_type:**
```python
# Try all workflow types
session = None
for wf_type in ['stock_research', 'index_research', 'opportunity_research']:
    try:
        session = timber_session_service.get_session(
            session_id=session_id,
            session_type=wf_type
        )
        if session:
            break
    except Exception:
        continue
```

---

### update_session()

```python
timber_session_service.update_session(
    session_id='abc-123',  # Required, keyword arg
    metadata={...}          # Data to update
)
```

**Key Points:**
- ✅ Use `session_id` keyword parameter
- ✅ Metadata is merged, not replaced
- ✅ Returns: None

---

## 🎯 Workflow Types vs Model Names

| Workflow Type (use this) | Model Name (don't use) |
|--------------------------|------------------------|
| `'stock_research'` | `'StockResearchSession'` |
| `'index_research'` | `'IndexResearchSession'` |
| `'opportunity_research'` | `'OpportunityResearchSession'` |

**Always use workflow type, never model name!**

---

## ✅ Complete Example

```python
from common.services.persistence import session_service as timber_session_service

# 1. Create session
session_id = timber_session_service.create_session(
    user_id='user-123',
    session_type='stock_research',
    metadata={
        'workflow_name': 'stock_research',
        'stock_symbol': 'AAPL',
        'status': 'created'
    }
)

# 2. Get session
session = timber_session_service.get_session(
    session_id=session_id,
    session_type='stock_research'
)

# 3. Update session
timber_session_service.update_session(
    session_id=session_id,
    metadata={
        **session['metadata'],
        'status': 'running',
        'task_id': 'task-123'
    }
)

# 4. Get updated session
session = timber_session_service.get_session(
    session_id=session_id,
    session_type='stock_research'
)
print(f"Status: {session['metadata']['status']}")
```

---

## ❌ Common Mistakes

### Mistake 1: Positional Arguments
```python
# WRONG ❌
session_id = timber_session_service.create_session(
    'user-123',           # Positional
    'stock_research',     # Positional
    {'metadata': {}}
)

# CORRECT ✅
session_id = timber_session_service.create_session(
    user_id='user-123',           # Keyword
    session_type='stock_research', # Keyword
    metadata={'metadata': {}}      # Keyword
)
```

### Mistake 2: Using Model Name
```python
# WRONG ❌
session_id = timber_session_service.create_session(
    user_id='user-123',
    session_type='StockResearchSession',  # Model name
    metadata={}
)

# CORRECT ✅
session_id = timber_session_service.create_session(
    user_id='user-123',
    session_type='stock_research',  # Workflow name
    metadata={}
)
```

### Mistake 3: Missing session_type in get_session()
```python
# WRONG ❌
session = timber_session_service.get_session(session_id)

# CORRECT ✅
session = timber_session_service.get_session(
    session_id=session_id,
    session_type='stock_research'
)
```

---

## 🔧 Fixed workflow_service.py

All methods now use the correct API:

```python
# create_workflow()
session_id = timber_session_service.create_session(
    user_id=user_id,
    session_type=workflow_name,  # ← workflow name, not model
    metadata=session_metadata
)

# get_status(), start_workflow(), trigger_transition(), cancel_workflow()
# All try each workflow type to find the session
for wf_type in ['stock_research', 'index_research', 'opportunity_research']:
    try:
        session = timber_session_service.get_session(
            session_id=session_id,
            session_type=wf_type
        )
        if session:
            break
    except Exception:
        continue
```

---

## 📝 Apply the Fix

```bash
# 1. Copy fixed file
cp workflow_service_final_fix.py services/workflow_service.py

# 2. Restart worker
docker-compose restart grove

# 3. Test
docker-compose exec grove python tests/example_workflow_service_usage.py
```

---

## ✅ Expected Results

All examples should now pass:

```
🆕 EXAMPLE 3: Creating a Workflow Session
✅ Workflow created successfully!
Session ID: abc-123-def-456

📊 EXAMPLE 4: Checking Initial Status  
✅ Status retrieved successfully!
Status: created
Workflow: stock_research

🚀 EXAMPLE 5: Starting Workflow
✅ Workflow started!
Task ID: task-123-456
```

---

**Quick Reference Card**  
**Version:** 1.0  
**Last Updated:** 2024  

Print this card and keep it handy when working with Timber's session service! 📋