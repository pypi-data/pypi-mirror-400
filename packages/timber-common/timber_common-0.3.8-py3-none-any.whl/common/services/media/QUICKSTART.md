# Quick Start Guide - Media Generation Service

## Installation

1. **Copy the service files** to your Timber project:
   ```bash
   cp -r common/services/media /path/to/timber/common/services/
   ```

2. **Install dependencies**:
   ```bash
   pip install google-generativeai google-genai pillow boto3
   ```

3. **Configure environment variables** in your `.env` file:
   ```bash
   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # DigitalOcean Spaces (already in your config)
   DIGITALOCEAN_SPACES_KEY=your_spaces_key
   DIGITALOCEAN_SPACES_SECRET=your_spaces_secret
   DIGITALOCEAN_SPACES_REGION=nyc3
   DIGITALOCEAN_SPACES_BUCKET=your_bucket_name
   ```

## Basic Usage (5 Minutes)

### 1. Initialize Service (One Time Setup)

```python
# In your application initialization (e.g., app.py or __init__.py)
from common.services.media import get_image_generation_service, StorageProvider
from common.utils.config import config

def init_media_service():
    """Initialize media generation service"""
    service = get_image_generation_service()
    
    # Configure Gemini API
    service.configure_gemini(config.GEMINI_API_KEY)
    
    # Configure Storage
    service.configure_storage(
        provider=StorageProvider.DIGITALOCEAN_SPACES,
        region=config.DIGITALOCEAN_SPACES_REGION,
        bucket=config.DIGITALOCEAN_SPACES_BUCKET,
        access_key=config.DIGITALOCEAN_SPACES_KEY,
        secret_key=config.DIGITALOCEAN_SPACES_SECRET
    )
    
    return service

# Call during app startup
media_service = init_media_service()
```

### 2. Generate and Upload Image

```python
from common.services.media import get_image_generation_service

# Get the service (already configured)
service = get_image_generation_service()

# Generate and upload in one call
result = service.generate_and_upload(
    prompt="A person achieving their retirement savings goal",
    object_key="goals/user_123/retirement.png"
)

print(f"Image URL: {result['url']}")
# Output: https://your-bucket.nyc3.digitaloceanspaces.com/goals/user_123/retirement.png
```

### 3. Integration with Your Existing Code

Replace your existing code:

```python
# OLD CODE (from goal_image_tasks.py)
# Configure API and storage for each task
genai.configure(api_key=Oak_Config.GEMINI_API_KEY)
s3_client = session.client('s3', ...)
# ... complex setup code ...

# Generate image
response = client.models.generate_content(...)
# ... extract image ...
# ... upload image ...
```

With new service:

```python
# NEW CODE (much simpler!)
from common.services.media import get_image_generation_service

service = get_image_generation_service()

result = service.generate_and_upload(
    prompt=f"Visual representation of financial goal: {goal.name}",
    object_key=f"goals/{goal.id}/{goal.name.replace(' ', '_').lower()}.png",
    metadata={
        "goal_id": str(goal.id),
        "user_id": str(goal.user_id),
        "goal_name": goal.name
    }
)

goal.image_url = result['url']
goal.image_prompt = result['prompt']
```

## Advanced Configuration (10 Minutes)

### Custom Image Size and Quality

```python
from common.services.media import ImageGenerationConfig, ImageSize, ImageQuality

config = ImageGenerationConfig(
    size=ImageSize.BANNER,        # 1920x1080 for banners
    quality=ImageQuality.HIGH,    # Best quality
    format="jpeg",                 # JPEG format
    jpeg_quality=95                # High JPEG quality
)

result = service.generate_and_upload(
    prompt="Portfolio growth visualization",
    object_key="portfolio/banner.jpg",
    config=config
)
```

### Different Themes

```python
from common.services.media import ImageTheme

# Professional style
config = ImageGenerationConfig(theme=ImageTheme.PROFESSIONAL)

# Illustration style
config = ImageGenerationConfig(theme=ImageTheme.ILLUSTRATION)

# Minimalist style
config = ImageGenerationConfig(theme=ImageTheme.MINIMALIST)
```

### Custom Brand Colors

```python
config = ImageGenerationConfig(
    brand_colors=["#0066CC", "#00AA66", "#FFD700"],
    theme=ImageTheme.PROFESSIONAL
)
```

## Celery Task Integration (15 Minutes)

Update your existing Celery task:

```python
# tasks/image_generation_tasks.py
from celery import shared_task
from common.services.media import get_image_generation_service, ImageGenerationConfig
from your_app.models import UserGoal
from your_app.database import db

@shared_task(bind=True, max_retries=5)
def generate_goal_image_task(self, goal_id: int):
    """Generate image for a user goal"""
    try:
        # Get service (already configured at app startup)
        service = get_image_generation_service()
        
        # Get goal
        goal = UserGoal.query.get(goal_id)
        if not goal:
            raise Exception(f"Goal {goal_id} not found")
        
        # Update status
        goal.image_generation_status = 'generating'
        db.session.commit()
        
        # Generate and upload
        result = service.generate_and_upload(
            prompt=f"Visual representation of financial goal: {goal.name}",
            object_key=f"goals/{goal.id}/{goal.name.replace(' ', '_').lower()}.png",
            metadata={
                "goal_id": str(goal.id),
                "user_id": str(goal.user_id),
                "goal_name": goal.name
            }
        )
        
        # Update goal
        goal.image_url = result['url']
        goal.image_prompt = result['prompt']
        goal.image_generation_status = 'completed'
        db.session.commit()
        
        return result['url']
        
    except Exception as e:
        if goal:
            goal.image_generation_status = 'failed'
            db.session.commit()
        raise self.retry(exc=e, countdown=300)
```

## Testing (5 Minutes)

### Run Unit Tests

```bash
pytest common/services/media/test_image_generation.py -v
```

### Test in Python REPL

```python
from common.services.media import get_image_generation_service, StorageProvider

# Initialize
service = get_image_generation_service()
service.configure_gemini("your_api_key")
service.configure_storage(
    provider=StorageProvider.DIGITALOCEAN_SPACES,
    region="nyc3",
    bucket="test-bucket",
    access_key="key",
    secret_key="secret"
)

# Test generation (without upload)
result = service.generate_image(
    prompt="A beautiful mountain sunset"
)

# Save locally
result['image'].save("test_image.png")
print("Generated successfully!")
```

## Common Patterns

### Pattern 1: Generate for User Goal
```python
def generate_goal_image(goal_id: int):
    service = get_image_generation_service()
    goal = Goal.query.get(goal_id)
    
    return service.generate_and_upload(
        prompt=f"Visual representation: {goal.name}",
        object_key=f"goals/{goal.user_id}/{goal.id}.png"
    )
```

### Pattern 2: Generate Portfolio Snapshot
```python
def generate_portfolio_image(portfolio_id: int):
    service = get_image_generation_service()
    portfolio = Portfolio.query.get(portfolio_id)
    
    config = ImageGenerationConfig(
        size=ImageSize.WIDE_CARD,
        quality=ImageQuality.HIGH
    )
    
    return service.generate_and_upload(
        prompt=f"Portfolio: {portfolio.name} - Diversified investments",
        object_key=f"portfolios/{portfolio.id}/snapshot.png",
        config=config
    )
```

### Pattern 3: Generate Thumbnail
```python
def generate_thumbnail(entity_id: int, description: str):
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.THUMBNAIL,
        quality=ImageQuality.LOW,
        format="webp"
    )
    
    return service.generate_and_upload(
        prompt=description,
        object_key=f"thumbnails/{entity_id}.webp",
        config=config
    )
```

## Troubleshooting

### Issue: "Gemini API not configured"
**Solution**: Make sure you call `configure_gemini()` after getting the service instance.

### Issue: "Storage not configured"
**Solution**: Make sure you call `configure_storage()` after getting the service instance.

### Issue: Images not uploading
**Solution**: 
1. Check your DigitalOcean Spaces credentials
2. Verify bucket exists
3. Check bucket permissions (should allow public read if public_access=True)

### Issue: Import errors
**Solution**: Make sure all dependencies are installed:
```bash
pip install google-generativeai google-genai pillow boto3
```

## Next Steps

1. **Read full documentation**: See `README.md` for comprehensive guide
2. **Explore examples**: Check `examples.py` for more use cases
3. **Review tests**: See `test_image_generation.py` for testing patterns
4. **Customize branding**: Update your `.env` with brand colors

## Support

- Documentation: `common/services/media/README.md`
- Examples: `common/services/media/examples.py`
- Tests: `common/services/media/test_image_generation.py`

---

**Time to Production**: ~30 minutes
- Setup: 5 minutes
- Integration: 15 minutes
- Testing: 10 minutes
