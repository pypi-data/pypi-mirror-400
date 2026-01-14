# GDPR Compliance in Timber

**Complete guide to data privacy, user rights, and GDPR compliance features**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Data Subject Rights](#data-subject-rights)
4. [Data Deletion](#data-deletion)
5. [Data Export](#data-export)
6. [Data Anonymization](#data-anonymization)
7. [Audit Trails](#audit-trails)
8. [Best Practices](#best-practices)
9. [Compliance Checklist](#compliance-checklist)

---

## Overview

Timber provides built-in GDPR compliance features to help you meet European data protection requirements. The system handles user data deletion, export, anonymization, and comprehensive audit trails.

### GDPR Rights Supported

Timber helps you implement:

- **Right to Access** - Export user data in structured format
- **Right to Erasure (Right to be Forgotten)** - Complete data deletion
- **Right to Data Portability** - Export data in machine-readable format
- **Right to Rectification** - Update incorrect data
- **Right to Restrict Processing** - Temporary data freezing
- **Data Minimization** - Store only necessary data
- **Purpose Limitation** - Clear data usage purposes

### Key Features

- **Cascade Deletion**: Automatically delete all related user data
- **Data Export**: Generate complete user data exports in JSON
- **Anonymization**: Replace user data with anonymized versions
- **Audit Trail**: Track all data access and modifications
- **Soft Delete Option**: Mark as deleted while retaining for compliance
- **Field-Level Control**: Configure which fields contain user data

---

## Quick Start

### Step 1: Enable GDPR Features

```python
from timber.common import initialize_timber

initialize_timber(
    model_config_dirs=['./data/models'],
    enable_gdpr=True,  # âœ… Enable GDPR features
    enable_encryption=True,  # Recommended for sensitive data
    gdpr_config={
        'export_format': 'json',  # or 'csv'
        'anonymize_deleted_users': True,  # Anonymize instead of hard delete
        'audit_all_access': True  # Track all data access
    }
)
```

### Step 2: Mark Models with User Data

```yaml
# data/models/user_models.yaml
models:
  - name: UserProfile
    table_name: user_profiles
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        nullable: false
        indexed: true
      
      - name: email
        type: String(255)
      
      - name: phone
        type: String(50)
      
      - name: preferences
        type: JSON
    
    mixins:
      - TimestampMixin
      - GDPRComplianceMixin  # âœ… Enable GDPR features
    
    gdpr_config:
      # Which field contains user identifier
      user_field: user_id
      
      # Fields to include in export
      export_fields:
        - email
        - phone
        - preferences
      
      # Fields to anonymize (if using anonymization)
      anonymize_fields:
        - email
        - phone
```

### Step 3: Use GDPR Service

```python
from timber.common.services.gdpr import gdpr_service
from timber.common.services.db_service import db_service

# Delete all user data
result = gdpr_service.delete_user_data(
    user_id='user-123',
    db_session=None,  # Will create its own session
    export_before_delete=True  # Export before deleting
)

print(f"Deleted: {result['deleted_count']} records")
print(f"Export saved to: {result['export_path']}")

# Or just export data
export = gdpr_service.export_user_data(
    user_id='user-123',
    db_session=None
)

print(f"Exported {len(export['data'])} datasets")
```

---

## Data Subject Rights

### Right to Access

Provide users with copies of their data:

```python
from timber.common.services.gdpr import gdpr_service

def handle_access_request(user_id: str) -> dict:
    """
    Handle GDPR Article 15 - Right of access by the data subject.
    
    Returns all personal data held about the user.
    """
    # Export all user data
    export = gdpr_service.export_user_data(
        user_id=user_id,
        db_session=None,
        format='json'  # or 'csv'
    )
    
    # Add metadata about data processing
    export['metadata'] = {
        'export_date': datetime.now().isoformat(),
        'data_controller': 'OakQuant Inc.',
        'purpose_of_processing': [
            'Investment research and analysis',
            'Portfolio management',
            'Market data aggregation'
        ],
        'data_recipients': [
            'Internal systems only',
            'No third-party sharing'
        ],
        'storage_period': 'Data retained while account is active + 2 years',
        'rights': [
            'Right to rectification',
            'Right to erasure',
            'Right to restrict processing',
            'Right to data portability',
            'Right to object'
        ]
    }
    
    return export

# Usage
user_export = handle_access_request('user-123')

# Save to file for user download
with open(f'exports/user_data_{user_id}.json', 'w') as f:
    json.dump(user_export, f, indent=2)
```

### Right to Erasure (Right to be Forgotten)

Delete all user data:

```python
def handle_erasure_request(user_id: str, reason: str = None) -> dict:
    """
    Handle GDPR Article 17 - Right to erasure ('right to be forgotten').
    
    Deletes all personal data unless there's a legal reason to retain it.
    """
    from timber.common.services.gdpr import gdpr_service
    from timber.common.services.db_service import db_service
    
    # Check if user has any legal obligations preventing deletion
    legal_hold = check_legal_hold(user_id)
    
    if legal_hold:
        return {
            'success': False,
            'reason': 'Data subject to legal hold',
            'details': legal_hold
        }
    
    # Delete user data
    result = gdpr_service.delete_user_data(
        user_id=user_id,
        db_session=None,
        export_before_delete=True,  # Export first for audit
        anonymize=False  # Complete deletion
    )
    
    # Log deletion for audit
    log_gdpr_action(
        user_id=user_id,
        action='right_to_erasure',
        reason=reason,
        result=result
    )
    
    return {
        'success': True,
        'deleted_count': result['deleted_count'],
        'tables_affected': result['tables'],
        'export_path': result.get('export_path'),
        'completed_at': datetime.now().isoformat()
    }

# Usage
result = handle_erasure_request(
    user_id='user-123',
    reason='User requested account deletion'
)
```

### Right to Data Portability

Export data in machine-readable format:

```python
def handle_portability_request(user_id: str, format: str = 'json') -> str:
    """
    Handle GDPR Article 20 - Right to data portability.
    
    Provide data in structured, commonly used, machine-readable format.
    """
    from timber.common.services.gdpr import gdpr_service
    
    # Export data
    export = gdpr_service.export_user_data(
        user_id=user_id,
        format=format  # json or csv
    )
    
    # Create portable format
    portable_data = {
        'format_version': '1.0',
        'generated_at': datetime.now().isoformat(),
        'user_id': user_id,
        'data': export['data']
    }
    
    # Save to file
    filename = f'portable_data_{user_id}_{datetime.now().strftime("%Y%m%d")}.{format}'
    filepath = f'exports/{filename}'
    
    if format == 'json':
        with open(filepath, 'w') as f:
            json.dump(portable_data, f, indent=2)
    elif format == 'csv':
        # Convert to CSV format
        import pandas as pd
        for dataset_name, records in export['data'].items():
            df = pd.DataFrame(records)
            csv_file = f'exports/{dataset_name}_{user_id}.csv'
            df.to_csv(csv_file, index=False)
    
    return filepath

# Usage
export_path = handle_portability_request('user-123', format='json')
print(f"Export available at: {export_path}")
```

### Right to Rectification

Update incorrect data:

```python
def handle_rectification_request(
    user_id: str,
    corrections: dict
) -> dict:
    """
    Handle GDPR Article 16 - Right to rectification.
    
    Update inaccurate or incomplete personal data.
    """
    from timber.common.models import get_model
    from timber.common.services.db_service import db_service
    
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if not profile:
            return {
                'success': False,
                'error': 'User profile not found'
            }
        
        # Store old values for audit
        old_values = {}
        updated_fields = []
        
        # Apply corrections
        for field, new_value in corrections.items():
            if hasattr(profile, field):
                old_values[field] = getattr(profile, field)
                setattr(profile, field, new_value)
                updated_fields.append(field)
        
        session.commit()
        
        # Log rectification
        log_gdpr_action(
            user_id=user_id,
            action='right_to_rectification',
            details={
                'updated_fields': updated_fields,
                'old_values': old_values,
                'new_values': corrections
            }
        )
        
        return {
            'success': True,
            'updated_fields': updated_fields,
            'completed_at': datetime.now().isoformat()
        }

# Usage
result = handle_rectification_request(
    user_id='user-123',
    corrections={
        'email': 'new_email@example.com',
        'phone': '+1-555-0199'
    }
)
```

### Right to Restrict Processing

Temporarily freeze data processing:

```python
def handle_restriction_request(
    user_id: str,
    reason: str
) -> dict:
    """
    Handle GDPR Article 18 - Right to restriction of processing.
    
    Mark user data as 'restricted' to prevent processing while
    maintaining storage for legal compliance.
    """
    from timber.common.models import get_model
    from timber.common.services.db_service import db_service
    
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if not profile:
            return {
                'success': False,
                'error': 'User profile not found'
            }
        
        # Mark as restricted
        profile.processing_restricted = True
        profile.restriction_reason = reason
        profile.restriction_date = datetime.now()
        
        session.commit()
        
        # Log restriction
        log_gdpr_action(
            user_id=user_id,
            action='right_to_restriction',
            reason=reason
        )
        
        return {
            'success': True,
            'restricted_at': profile.restriction_date.isoformat(),
            'reason': reason
        }

# Usage
result = handle_restriction_request(
    user_id='user-123',
    reason='User disputes data accuracy'
)

# Check if processing is restricted before operations
def can_process_user_data(user_id: str) -> bool:
    """Check if user data processing is restricted."""
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if profile and profile.processing_restricted:
            return False
        
        return True
```

---

## Data Deletion

### Cascade Deletion

Timber automatically deletes all related user data:

```python
from timber.common.services.gdpr import gdpr_service

def complete_user_deletion(user_id: str):
    """
    Delete all user data across all tables.
    
    Timber automatically:
    1. Finds all models with user_id fields
    2. Deletes records in correct order (respecting foreign keys)
    3. Handles soft delete if configured
    4. Creates audit trail
    """
    result = gdpr_service.delete_user_data(
        user_id=user_id,
        db_session=None,
        export_before_delete=True  # âœ… Always export first
    )
    
    print(f"Deletion Summary:")
    print(f"  Records deleted: {result['deleted_count']}")
    print(f"  Tables affected: {len(result['tables'])}")
    print(f"  Export saved: {result['export_path']}")
    
    for table_name, count in result['tables'].items():
        print(f"    {table_name}: {count} records")
    
    return result

# Usage
complete_user_deletion('user-123')
```

### Soft Delete

Mark records as deleted without removing them:

```yaml
# Configure soft delete in model
models:
  - name: UserData
    table_name: user_data
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
      
      - name: deleted_at
        type: DateTime
        nullable: true  # NULL = not deleted
      
      - name: deletion_reason
        type: String(500)
        nullable: true
    
    mixins:
      - TimestampMixin
      - SoftDeleteMixin  # âœ… Enable soft delete
      - GDPRComplianceMixin
```

```python
# Soft delete implementation
def soft_delete_user(user_id: str, reason: str = None):
    """
    Mark user as deleted without removing data.
    
    Useful for:
    - Compliance audit trails
    - Legal hold requirements
    - Accidental deletion recovery
    """
    result = gdpr_service.delete_user_data(
        user_id=user_id,
        db_session=None,
        soft_delete=True,  # âœ… Soft delete
        deletion_metadata={
            'reason': reason,
            'requested_by': 'user',
            'deleted_at': datetime.now().isoformat()
        }
    )
    
    return result

# Restore soft-deleted user
def restore_user(user_id: str):
    """Restore soft-deleted user."""
    from timber.common.models import get_model
    
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if profile and profile.deleted_at:
            profile.deleted_at = None
            profile.deletion_reason = None
            session.commit()
            
            return {'success': True}
    
    return {'success': False, 'error': 'User not found or not deleted'}
```

### Selective Deletion

Delete specific data categories:

```python
def delete_user_research_data(user_id: str):
    """
    Delete only research data, keep account and portfolio.
    """
    from timber.common.models import get_model
    from timber.common.services.db_service import db_service
    
    # Models to delete
    models_to_delete = [
        'ResearchSession',
        'ResearchNote',
        'Analysis'
    ]
    
    deleted_count = 0
    
    with db_service.session_scope() as session:
        for model_name in models_to_delete:
            Model = get_model(model_name)
            if Model:
                count = session.query(Model)\
                    .filter_by(user_id=user_id)\
                    .delete()
                deleted_count += count
        
        session.commit()
    
    # Also delete vector embeddings for this user's research
    gdpr_service.delete_user_vector_embeddings(
        user_id=user_id,
        source_types=['research_notes', 'research_sessions']
    )
    
    return {
        'deleted_count': deleted_count,
        'categories': models_to_delete
    }
```

### Automated Deletion

Schedule automatic deletion of inactive accounts:

```python
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

def delete_inactive_accounts():
    """
    Delete accounts inactive for > 2 years (GDPR recommendation).
    """
    from timber.common.models import get_model
    from timber.common.services.db_service import db_service
    
    UserProfile = get_model('UserProfile')
    cutoff_date = datetime.now() - timedelta(days=730)  # 2 years
    
    with db_service.session_scope() as session:
        inactive_users = session.query(UserProfile)\
            .filter(UserProfile.last_activity < cutoff_date)\
            .filter(UserProfile.deletion_scheduled == True)\
            .all()
        
        for user in inactive_users:
            # Send final warning email
            send_deletion_warning(user.user_id, user.email)
            
            # Wait 30 days, then delete
            schedule_deletion(user.user_id, days=30)

def schedule_deletion(user_id: str, days: int = 30):
    """Schedule user deletion."""
    deletion_date = datetime.now() + timedelta(days=days)
    
    # Store in database
    with db_service.session_scope() as session:
        UserProfile = get_model('UserProfile')
        user = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if user:
            user.deletion_scheduled = True
            user.deletion_date = deletion_date
            session.commit()

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    delete_inactive_accounts,
    'cron',
    day_of_week='mon',  # Run every Monday
    hour=2,
    minute=0
)
scheduler.start()
```

---

## Data Export

### JSON Export

Export all user data in JSON format:

```python
from timber.common.services.gdpr import gdpr_service

def export_user_data_json(user_id: str) -> dict:
    """
    Export complete user data in JSON format.
    
    Returns structured JSON with all user information.
    """
    export = gdpr_service.export_user_data(
        user_id=user_id,
        format='json'
    )
    
    # Structure:
    # {
    #     'user_id': 'user-123',
    #     'export_date': '2025-10-19T10:00:00Z',
    #     'data': {
    #         'user_profiles': [{...}],
    #         'research_sessions': [{...}],
    #         'portfolios': [{...}],
    #         ...
    #     }
    # }
    
    return export

# Save to file
export = export_user_data_json('user-123')

with open(f'user_data_{user_id}.json', 'w') as f:
    json.dump(export, f, indent=2, default=str)
```

### CSV Export

Export data in CSV format:

```python
import pandas as pd

def export_user_data_csv(user_id: str, output_dir: str = 'exports'):
    """
    Export user data as multiple CSV files (one per table).
    """
    export = gdpr_service.export_user_data(
        user_id=user_id,
        format='json'  # Get as JSON first
    )
    
    # Convert each dataset to CSV
    for table_name, records in export['data'].items():
        if records:
            df = pd.DataFrame(records)
            
            # Clean column names
            df.columns = [col.replace('_', ' ').title() for col in df.columns]
            
            # Save to CSV
            csv_path = f'{output_dir}/{user_id}_{table_name}.csv'
            df.to_csv(csv_path, index=False)
            
            print(f"âœ… Exported {len(df)} rows to {csv_path}")

# Usage
export_user_data_csv('user-123', output_dir='user_exports')
```

### Scheduled Exports

Automatically generate exports:

```python
def schedule_monthly_exports():
    """
    Generate monthly data exports for all users.
    
    Useful for compliance and backup purposes.
    """
    from timber.common.models import get_model
    from timber.common.services.db_service import db_service
    
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        users = session.query(UserProfile).all()
        
        for user in users:
            try:
                # Generate export
                export = gdpr_service.export_user_data(
                    user_id=user.user_id
                )
                
                # Save to secure storage
                save_path = f'backups/{datetime.now().strftime("%Y%m")}/user_{user.user_id}.json'
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'w') as f:
                    json.dump(export, f, default=str)
                
                print(f"âœ… Exported data for {user.user_id}")
                
            except Exception as e:
                print(f"â Failed export for {user.user_id}: {e}")

# Schedule monthly
scheduler = BackgroundScheduler()
scheduler.add_job(
    schedule_monthly_exports,
    'cron',
    day=1,  # First day of month
    hour=1,
    minute=0
)
scheduler.start()
```

---

## Data Anonymization

### Anonymize User Data

Replace personal data with anonymized versions:

```python
def anonymize_user(user_id: str):
    """
    Anonymize user data instead of deleting.
    
    Useful when:
    - Need to retain data for analytics
    - Legal requirements to keep records
    - Want to preserve historical data
    """
    from timber.common.services.gdpr import gdpr_service
    
    result = gdpr_service.anonymize_user_data(
        user_id=user_id,
        db_session=None
    )
    
    # User data is now:
    # - Email: anon_abc123@example.com
    # - Name: Anonymous User
    # - Phone: ANONYMIZED
    # - Other PII: Replaced with generic values
    
    return result

# Custom anonymization rules
def anonymize_with_custom_rules(user_id: str):
    """Anonymize with specific rules."""
    from timber.common.models import get_model
    from timber.common.services.db_service import db_service
    import hashlib
    
    UserProfile = get_model('UserProfile')
    
    # Generate consistent anonymous ID
    anon_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if profile:
            # Anonymize fields
            profile.email = f'anon_{anon_id}@anonymized.local'
            profile.phone = 'ANONYMIZED'
            profile.name = f'Anonymous User {anon_id}'
            
            # Keep non-PII data
            # - Created date preserved
            # - Subscription level preserved
            # - Usage statistics preserved
            
            session.commit()
            
            return {'success': True, 'anon_id': anon_id}
```

### Anonymization Strategies

Different approaches for different data types:

```python
class AnonymizationStrategy:
    """Different anonymization strategies."""
    
    @staticmethod
    def email(email: str) -> str:
        """Anonymize email address."""
        import hashlib
        hash_part = hashlib.md5(email.encode()).hexdigest()[:8]
        return f"anon_{hash_part}@anonymized.local"
    
    @staticmethod
    def phone(phone: str) -> str:
        """Anonymize phone number."""
        return "ANONYMIZED"
    
    @staticmethod
    def name(name: str) -> str:
        """Anonymize name."""
        import hashlib
        hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"Anonymous User {hash_part}"
    
    @staticmethod
    def address(address: str) -> str:
        """Anonymize address - keep only city."""
        # Extract city if possible
        parts = address.split(',')
        if len(parts) >= 2:
            city = parts[-2].strip()
            return f"[REDACTED], {city}"
        return "[REDACTED]"
    
    @staticmethod
    def date_of_birth(dob: datetime) -> datetime:
        """Anonymize DOB - keep only year."""
        return datetime(dob.year, 1, 1)
    
    @staticmethod
    def financial_data(amount: float) -> str:
        """Anonymize financial amounts."""
        # Round to nearest $10,000
        rounded = round(amount, -4)
        return f"~${rounded:,.0f}"

# Apply anonymization
def apply_anonymization_strategies(user_id: str):
    """Apply different strategies to different fields."""
    from timber.common.models import get_model
    
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if profile:
            profile.email = AnonymizationStrategy.email(profile.email)
            profile.phone = AnonymizationStrategy.phone(profile.phone)
            profile.name = AnonymizationStrategy.name(profile.name)
            
            if profile.address:
                profile.address = AnonymizationStrategy.address(profile.address)
            
            if profile.date_of_birth:
                profile.date_of_birth = AnonymizationStrategy.date_of_birth(
                    profile.date_of_birth
                )
            
            session.commit()
```

---

## Audit Trails

### Automatic Audit Logging

Track all GDPR-related operations:

```yaml
# Enable audit logging
models:
  - name: GDPRAuditLog
    table_name: gdpr_audit_log
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        nullable: false
        indexed: true
      
      - name: action
        type: String(50)
        nullable: false
      
      - name: details
        type: JSON
      
      - name: performed_by
        type: String(36)
      
      - name: ip_address
        type: String(45)
      
      - name: timestamp
        type: DateTime
        nullable: false
    
    indexes:
      - columns: [user_id, timestamp]
      - columns: [action, timestamp]
```

```python
from timber.common.models import get_model

def log_gdpr_action(
    user_id: str,
    action: str,
    details: dict = None,
    performed_by: str = None,
    ip_address: str = None
):
    """Log GDPR compliance action."""
    GDPRAuditLog = get_model('GDPRAuditLog')
    
    with db_service.session_scope() as session:
        log = GDPRAuditLog(
            user_id=user_id,
            action=action,
            details=details or {},
            performed_by=performed_by or 'system',
            ip_address=ip_address,
            timestamp=datetime.now()
        )
        session.add(log)
        session.commit()

# Usage
log_gdpr_action(
    user_id='user-123',
    action='data_export',
    details={
        'format': 'json',
        'records_exported': 1250,
        'file_size_mb': 2.5
    },
    performed_by='user-123',
    ip_address='192.168.1.100'
)
```

### Query Audit Logs

Retrieve audit history:

```python
def get_user_gdpr_history(user_id: str):
    """Get complete GDPR action history for user."""
    GDPRAuditLog = get_model('GDPRAuditLog')
    
    with db_service.session_scope() as session:
        logs = session.query(GDPRAuditLog)\
            .filter_by(user_id=user_id)\
            .order_by(GDPRAuditLog.timestamp.desc())\
            .all()
        
        history = []
        for log in logs:
            history.append({
                'action': log.action,
                'timestamp': log.timestamp.isoformat(),
                'performed_by': log.performed_by,
                'details': log.details
            })
        
        return history

# Get history
history = get_user_gdpr_history('user-123')

for action in history:
    print(f"{action['timestamp']}: {action['action']}")
    print(f"  By: {action['performed_by']}")
    print(f"  Details: {action['details']}")
```

### Audit Reports

Generate compliance reports:

```python
def generate_gdpr_compliance_report(
    start_date: datetime,
    end_date: datetime
) -> dict:
    """
    Generate GDPR compliance report for date range.
    """
    GDPRAuditLog = get_model('GDPRAuditLog')
    
    with db_service.session_scope() as session:
        logs = session.query(GDPRAuditLog)\
            .filter(GDPRAuditLog.timestamp >= start_date)\
            .filter(GDPRAuditLog.timestamp <= end_date)\
            .all()
        
        # Aggregate statistics
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_requests': len(logs),
            'requests_by_type': {},
            'average_response_time': None,
            'users_affected': set()
        }
        
        for log in logs:
            # Count by type
            action = log.action
            report['requests_by_type'][action] = \
                report['requests_by_type'].get(action, 0) + 1
            
            # Track unique users
            report['users_affected'].add(log.user_id)
        
        report['unique_users'] = len(report['users_affected'])
        report['users_affected'] = list(report['users_affected'])
        
        return report

# Generate monthly report
report = generate_gdpr_compliance_report(
    start_date=datetime(2025, 10, 1),
    end_date=datetime(2025, 10, 31)
)

print(f"GDPR Compliance Report:")
print(f"  Total requests: {report['total_requests']}")
print(f"  Unique users: {report['unique_users']}")
print(f"\n  Requests by type:")
for action, count in report['requests_by_type'].items():
    print(f"    {action}: {count}")
```

---

## Best Practices

### 1. Always Export Before Delete

```python
def safe_delete_user(user_id: str):
    """Always export data before deletion."""
    
    # âœ… Export first
    export = gdpr_service.export_user_data(user_id=user_id)
    
    # Save export securely
    save_path = f'gdpr_exports/deletion/{user_id}_{datetime.now().strftime("%Y%m%d")}.json'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'w') as f:
        json.dump(export, f, default=str)
    
    # âœ… Then delete
    result = gdpr_service.delete_user_data(
        user_id=user_id,
        export_before_delete=False  # Already exported
    )
    
    return result
```

### 2. Implement Retention Policies

```python
class DataRetentionPolicy:
    """Define and enforce data retention policies."""
    
    # Retention periods by data type
    RETENTION_PERIODS = {
        'user_profiles': 730,  # 2 years after last activity
        'research_sessions': 1095,  # 3 years
        'transactions': 2555,  # 7 years (legal requirement)
        'audit_logs': 1825,  # 5 years
    }
    
    @classmethod
    def should_delete(cls, data_type: str, last_activity: datetime) -> bool:
        """Check if data should be deleted based on policy."""
        retention_days = cls.RETENTION_PERIODS.get(data_type, 365)
        cutoff = datetime.now() - timedelta(days=retention_days)
        return last_activity < cutoff
    
    @classmethod
    def enforce_retention_policy(cls):
        """Enforce retention policy across all data types."""
        for data_type, retention_days in cls.RETENTION_PERIODS.items():
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Find expired records
            Model = get_model(data_type)
            if not Model:
                continue
            
            with db_service.session_scope() as session:
                expired = session.query(Model)\
                    .filter(Model.last_activity < cutoff_date)\
                    .all()
                
                for record in expired:
                    # Archive before deletion
                    archive_record(record)
                    
                    # Delete
                    session.delete(record)
                
                session.commit()
                
                print(f"Deleted {len(expired)} expired {data_type} records")
```

### 3. Minimize Data Collection

Only collect necessary data:

```python
# â Bad: Collecting unnecessary data
class UserProfile:
    email = Column(String)  # Necessary
    phone = Column(String)  # Necessary
    favorite_color = Column(String)  # â Unnecessary!
    shoe_size = Column(Integer)  # â Unnecessary!

# âœ… Good: Only necessary data
class UserProfile:
    email = Column(String)  # Necessary for communication
    phone = Column(String)  # Necessary for 2FA
    # Only collect what you need!
```

### 4. Document Data Usage

```python
DATA_USAGE_PURPOSES = {
    'email': [
        'Account communication',
        'Password reset',
        'Security alerts'
    ],
    'phone': [
        'Two-factor authentication',
        'Security verification'
    ],
    'research_data': [
        'Investment analysis',
        'Portfolio recommendations',
        'Service improvement'
    ]
}

def document_data_usage():
    """Generate data usage documentation for privacy policy."""
    usage_doc = {
        'last_updated': datetime.now().isoformat(),
        'purposes': DATA_USAGE_PURPOSES,
        'retention_periods': DataRetentionPolicy.RETENTION_PERIODS,
        'third_party_sharing': {
            'analytics': 'Google Analytics (anonymized)',
            'email': 'SendGrid (for transactional emails)',
            'payment': 'Stripe (for payment processing)'
        },
        'user_rights': [
            'Right to access',
            'Right to rectification',
            'Right to erasure',
            'Right to restrict processing',
            'Right to data portability',
            'Right to object'
        ]
    }
    
    return usage_doc
```

### 5. Regular Compliance Audits

```python
def run_compliance_audit():
    """
    Run comprehensive GDPR compliance audit.
    """
    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'checks': []
    }
    
    # Check 1: All models have GDPR mixins where needed
    audit_results['checks'].append({
        'check': 'GDPR Mixins',
        'status': verify_gdpr_mixins(),
        'details': 'All user data models have GDPRComplianceMixin'
    })
    
    # Check 2: Audit logs are being created
    audit_results['checks'].append({
        'check': 'Audit Logging',
        'status': verify_audit_logging(),
        'details': 'All GDPR actions are logged'
    })
    
    # Check 3: Retention policies are enforced
    audit_results['checks'].append({
        'check': 'Data Retention',
        'status': verify_retention_policies(),
        'details': 'Retention policies are active and enforced'
    })
    
    # Check 4: Encryption is enabled for sensitive fields
    audit_results['checks'].append({
        'check': 'Data Encryption',
        'status': verify_encryption(),
        'details': 'All PII fields are encrypted'
    })
    
    # Check 5: Data export functionality works
    audit_results['checks'].append({
        'check': 'Data Export',
        'status': test_data_export(),
        'details': 'Export functionality tested and working'
    })
    
    # Generate report
    passed = sum(1 for check in audit_results['checks'] if check['status'])
    total = len(audit_results['checks'])
    
    audit_results['summary'] = {
        'passed': passed,
        'total': total,
        'compliance_score': (passed / total) * 100
    }
    
    return audit_results

# Run monthly audit
audit = run_compliance_audit()
print(f"Compliance Score: {audit['summary']['compliance_score']}%")
```

---

## Compliance Checklist

### Implementation Checklist

- [ ] GDPRComplianceMixin added to all user data models
- [ ] Data export functionality implemented
- [ ] Data deletion with cascade implemented
- [ ] Anonymization option available
- [ ] Audit logging for all GDPR actions
- [ ] Retention policies defined and enforced
- [ ] Privacy policy updated with data usage
- [ ] User consent mechanisms in place
- [ ] Data breach notification procedure defined
- [ ] DPO (Data Protection Officer) designated
- [ ] GDPR training completed for staff
- [ ] Regular compliance audits scheduled

### User Rights Checklist

- [ ] Right to Access: Export functionality
- [ ] Right to Rectification: Update endpoints
- [ ] Right to Erasure: Delete functionality
- [ ] Right to Restrict Processing: Freeze functionality
- [ ] Right to Data Portability: Structured export
- [ ] Right to Object: Opt-out mechanisms
- [ ] Automated Decision-Making: Human review option

### Technical Measures Checklist

- [ ] Encryption for data at rest
- [ ] Encryption for data in transit (HTTPS)
- [ ] Field-level encryption for sensitive data
- [ ] Access controls implemented
- [ ] Audit trails for all data access
- [ ] Secure deletion procedures
- [ ] Backup and recovery procedures
- [ ] Incident response plan

### Documentation Checklist

- [ ] Privacy policy published
- [ ] Data processing records maintained
- [ ] Data mapping completed
- [ ] Third-party processors identified
- [ ] Data transfer agreements in place
- [ ] User consent records maintained
- [ ] Retention policy documented
- [ ] Security measures documented

---

## Complete Example

```python
# Complete GDPR implementation example

from timber.common import initialize_timber
from timber.common.models import get_model
from timber.common.services.gdpr import gdpr_service
from timber.common.services.db_service import db_service
from datetime import datetime, timedelta
import json

# Initialize with GDPR features
initialize_timber(
    model_config_dirs=['./data/models'],
    enable_gdpr=True,
    enable_encryption=True,
    gdpr_config={
        'export_format': 'json',
        'anonymize_deleted_users': True,
        'audit_all_access': True
    }
)

class GDPRComplianceManager:
    """Comprehensive GDPR compliance manager."""
    
    def __init__(self):
        self.gdpr_service = gdpr_service
        self.audit_log = []
    
    def handle_access_request(self, user_id: str) -> str:
        """Handle right to access request."""
        export = self.gdpr_service.export_user_data(user_id=user_id)
        
        # Save export
        filename = f'gdpr_export_{user_id}_{datetime.now().strftime("%Y%m%d")}.json'
        with open(f'exports/{filename}', 'w') as f:
            json.dump(export, f, indent=2, default=str)
        
        # Log action
        self._log_action(user_id, 'access_request', {'filename': filename})
        
        return filename
    
    def handle_deletion_request(
        self,
        user_id: str,
        reason: str = None
    ) -> dict:
        """Handle right to erasure request."""
        # Export before deletion
        export_file = self.handle_access_request(user_id)
        
        # Delete data
        result = self.gdpr_service.delete_user_data(
            user_id=user_id,
            export_before_delete=False  # Already exported
        )
        
        # Log action
        self._log_action(
            user_id,
            'deletion_request',
            {
                'reason': reason,
                'export_file': export_file,
                'deleted_count': result['deleted_count']
            }
        )
        
        return result
    
    def handle_rectification_request(
        self,
        user_id: str,
        corrections: dict
    ) -> dict:
        """Handle right to rectification request."""
        UserProfile = get_model('UserProfile')
        
        with db_service.session_scope() as session:
            profile = session.query(UserProfile)\
                .filter_by(user_id=user_id)\
                .first()
            
            if not profile:
                return {'success': False, 'error': 'User not found'}
            
            # Apply corrections
            for field, value in corrections.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            session.commit()
            
            # Log action
            self._log_action(
                user_id,
                'rectification_request',
                {'corrections': corrections}
            )
            
            return {'success': True}
    
    def enforce_retention_policy(self):
        """Enforce data retention policies."""
        UserProfile = get_model('UserProfile')
        cutoff_date = datetime.now() - timedelta(days=730)  # 2 years
        
        with db_service.session_scope() as session:
            inactive_users = session.query(UserProfile)\
                .filter(UserProfile.last_activity < cutoff_date)\
                .all()
            
            for user in inactive_users:
                # Anonymize instead of delete
                self.gdpr_service.anonymize_user_data(
                    user_id=user.user_id
                )
                
                self._log_action(
                    user.user_id,
                    'retention_policy',
                    {'reason': 'Inactive for 2+ years'}
                )
    
    def generate_compliance_report(self, days: int = 30) -> dict:
        """Generate GDPR compliance report."""
        start_date = datetime.now() - timedelta(days=days)
        
        GDPRAuditLog = get_model('GDPRAuditLog')
        
        with db_service.session_scope() as session:
            logs = session.query(GDPRAuditLog)\
                .filter(GDPRAuditLog.timestamp >= start_date)\
                .all()
            
            report = {
                'period_days': days,
                'total_requests': len(logs),
                'requests_by_type': {},
                'unique_users': len(set(log.user_id for log in logs))
            }
            
            for log in logs:
                action = log.action
                report['requests_by_type'][action] = \
                    report['requests_by_type'].get(action, 0) + 1
            
            return report
    
    def _log_action(self, user_id: str, action: str, details: dict):
        """Log GDPR action."""
        GDPRAuditLog = get_model('GDPRAuditLog')
        
        with db_service.session_scope() as session:
            log = GDPRAuditLog(
                user_id=user_id,
                action=action,
                details=details,
                timestamp=datetime.now()
            )
            session.add(log)
            session.commit()

# Usage
if __name__ == '__main__':
    manager = GDPRComplianceManager()
    
    # Handle access request
    export_file = manager.handle_access_request('user-123')
    print(f"âœ… Data exported to: {export_file}")
    
    # Handle rectification
    result = manager.handle_rectification_request(
        user_id='user-123',
        corrections={'email': 'newemail@example.com'}
    )
    print(f"âœ… Data rectified: {result}")
    
    # Generate compliance report
    report = manager.generate_compliance_report(days=30)
    print(f"âœ… Compliance report:")
    print(f"   Total requests: {report['total_requests']}")
    print(f"   Unique users: {report['unique_users']}")
```

---

## Summary

**Key Takeaways:**

âœ… **Automated Compliance** - Built-in GDPR features  
âœ… **User Rights** - All 7 key rights supported  
âœ… **Data Export** - JSON/CSV formats  
âœ… **Safe Deletion** - Cascade with export  
âœ… **Anonymization** - Alternative to deletion  
âœ… **Audit Trails** - Complete logging  
âœ… **Retention Policies** - Automated enforcement  

**Next Steps:**

1. Enable GDPR features in initialization
2. Add GDPRComplianceMixin to user data models
3. Implement access request handlers
4. Set up deletion procedures
5. Configure retention policies
6. Enable audit logging
7. Generate compliance reports

---

**Created:** October 19, 2025  
**Version:** 0.2.0  
**Word Count:** ~6,500 words  
**Status:** âœ… Complete