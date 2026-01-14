# timber/common/services/media/README.md
# Media Generation Service

Comprehensive AI-powered media generation and cloud storage service for the Timber ecosystem.

## Features

- **AI Image Generation**: Generate professional images using Google Gemini
- **Cloud Storage**: Upload to DigitalOcean Spaces or AWS S3
- **Configurable**: Extensive configuration options for size, quality, theme, and branding
- **Financial Application Optimized**: Defaults tuned for investment/financial platforms
- **Singleton Pattern**: Efficient resource management with single service instance
- **Type Safe**: Full type hints and enum-based configuration

## Installation

### Required Dependencies

```bash
pip install google-generativeai google-genai pillow boto3 python-dotenv
```

### Environment Variables

Add to your `.env` file:

```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# DigitalOcean Spaces (or AWS S3)
DIGITALOCEAN_SPACES_KEY=your_spaces_access_key
DIGITALOCEAN_SPACES_SECRET=your_spaces_secret_key
DIGITALOCEAN_SPACES_REGION=nyc3
DIGITALOCEAN_SPACES_BUCKET=your_bucket_name
DIGITALOCEAN_SPACES_CDN=your_cdn_url  # Optional

# Brand Configuration
BRAND_PRIMARY_COLOR=#0066CC
BRAND_SECONDARY_COLOR=#00AA66
BRAND_STYLE=professional
```

## Quick Start

### Basic Usage

```python
from common.services.media import get_image_generation_service, ImageGenerationConfig
from common.utils.config import config

# Get service instance
image_service = get_image_generation_service()

# Configure service
image_service.configure_gemini(config.GEMINI_API_KEY)
image_service.configure_storage(
    provider=StorageProvider.DIGITALOCEAN_SPACES,
    region=config.DIGITALOCEAN_SPACES_REGION,
    bucket=config.DIGITALOCEAN_SPACES_BUCKET,
    access_key=config.DIGITALOCEAN_SPACES_KEY,
    secret_key=config.DIGITALOCEAN_SPACES_SECRET
)

# Generate and upload image
result = image_service.generate_and_upload(
    prompt="A person achieving their retirement savings goal",
    object_key="goals/retirement/user_123.png"
)

print(f"Image URL: {result['url']}")
```

### Using Configuration

```python
from common.services.media import (
    ImageGenerationConfig,
    ImageSize,
    ImageQuality,
    ImageTheme
)

# Create custom configuration
config = ImageGenerationConfig(
    size=ImageSize.CARD,
    quality=ImageQuality.HIGH,
    theme=ImageTheme.PROFESSIONAL,
    brand_colors=["#0066CC", "#00AA66"],
    format="png",
    compression_level=9
)

# Generate with custom config
result = image_service.generate_and_upload(
    prompt="A growing investment portfolio",
    object_key="portfolios/growth_visual.png",
    config=config
)
```

## Configuration Options

### Image Sizes

```python
from common.services.media import ImageSize

ImageSize.THUMBNAIL    # 256x256 - Small thumbnails
ImageSize.CARD         # 512x512 - Card displays
ImageSize.STANDARD     # 1024x1024 - Standard (default)
ImageSize.BANNER       # 1920x1080 - Hero/banner images
ImageSize.WIDE_CARD    # 1280x720 - Wide format
ImageSize.PORTRAIT     # 768x1024 - Portrait orientation
ImageSize.CUSTOM       # Custom dimensions
```

### Image Quality

```python
from common.services.media import ImageQuality

ImageQuality.LOW       # Faster generation, smaller files
ImageQuality.MEDIUM    # Balanced (default)
ImageQuality.HIGH      # Best quality, larger files
```

### Image Themes

```python
from common.services.media import ImageTheme

ImageTheme.REALISTIC      # Photo-realistic (default)
ImageTheme.PROFESSIONAL   # Corporate/professional
ImageTheme.ILLUSTRATION   # Illustrated style
ImageTheme.ABSTRACT       # Abstract/conceptual
ImageTheme.MINIMALIST     # Clean, minimal
ImageTheme.FUTURISTIC     # Modern/tech
ImageTheme.INFOGRAPHIC    # Data visualization
ImageTheme.VINTAGE        # Classic/retro
```

### Storage Providers

```python
from common.services.media import StorageProvider

StorageProvider.DIGITALOCEAN_SPACES  # DigitalOcean Spaces
StorageProvider.AWS_S3               # Amazon S3
StorageProvider.LOCAL                # Local storage (dev/testing)
```

## Advanced Usage

### Custom Dimensions

```python
config = ImageGenerationConfig(
    size=ImageSize.CUSTOM,
    custom_width=1600,
    custom_height=900,
    format="jpeg",
    jpeg_quality=90
)
```

### Brand Colors

```python
config = ImageGenerationConfig(
    brand_colors=["#0066CC", "#00AA66", "#FFD700"],
    theme=ImageTheme.PROFESSIONAL
)
```

### Without Financial Enhancement

```python
# Generate generic image without financial context
result = image_service.generate_and_upload(
    prompt="A beautiful sunset over mountains",
    object_key="generic/sunset.png",
    enhance_for_finance=False  # Disable financial enhancements
)
```

### Generate Only (No Upload)

```python
# Generate image without uploading
result = image_service.generate_image(
    prompt="Investment growth visualization",
    config=config
)

# Access PIL Image object
pil_image = result['image']
pil_image.save("/local/path/image.png")
```

### Upload Existing Image

```python
from PIL import Image

# Load existing image
image = Image.open("path/to/image.png")

# Upload to cloud storage
url = image_service.upload_image(
    image=image,
    object_key="portfolios/existing_image.png",
    metadata={"source": "manual_upload", "category": "portfolio"}
)
```

### Delete Image

```python
# Delete image from storage
success = image_service.delete_image("goals/old_image.png")
```

## Integration with Celery Tasks

### Example Task Implementation

```python
# tasks/media_tasks.py
from celery import shared_task
from common.services.media import get_image_generation_service, ImageGenerationConfig
from common.utils.config import config
from your_app.models import UserGoal

@shared_task(bind=True, max_retries=5)
def generate_goal_image_task(self, goal_id: int):
    """
    Celery task to generate image for a user goal.
    """
    try:
        # Get service
        image_service = get_image_generation_service()
        
        # Configure (only needed once, but safe to call multiple times)
        image_service.configure_gemini(config.GEMINI_API_KEY)
        image_service.configure_storage(
            provider=StorageProvider.DIGITALOCEAN_SPACES,
            region=config.DIGITALOCEAN_SPACES_REGION,
            bucket=config.DIGITALOCEAN_SPACES_BUCKET,
            access_key=config.DIGITALOCEAN_SPACES_KEY,
            secret_key=config.DIGITALOCEAN_SPACES_SECRET
        )
        
        # Get goal from database
        goal = UserGoal.query.get(goal_id)
        if not goal:
            raise Exception(f"Goal {goal_id} not found")
        
        # Update status
        goal.image_generation_status = 'generating'
        db.session.commit()
        
        # Generate and upload
        result = image_service.generate_and_upload(
            prompt=f"Visual representation of financial goal: {goal.name}",
            object_key=f"goals/{goal.id}/{goal.name.replace(' ', '_').lower()}.png",
            metadata={
                "goal_id": str(goal.id),
                "user_id": str(goal.user_id),
                "goal_name": goal.name
            }
        )
        
        # Update goal with image URL
        goal.image_url = result['url']
        goal.image_prompt = result['prompt']
        goal.image_generation_status = 'completed'
        db.session.commit()
        
        return result['url']
        
    except Exception as e:
        if goal:
            goal.image_generation_status = 'failed'
            db.session.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=300)
```

## Configuration Management

### Using Config Helper Methods

```python
from common.utils.config import config
from common.services.media.config_helpers import extend_config_class

# Extend Config class with media methods
extend_config_class(Config)

# Now you can use convenience methods
gemini_config = config.get_gemini_config()
storage_config = config.get_media_storage_config()
brand_config = config.get_brand_config()

# Validate configuration
validation = config.validate_media_config()
if not validation['gemini_configured']:
    print("Gemini API key not configured!")
```

### Complete Configuration

```python
from common.services.media import get_image_generation_service, StorageProvider
from common.utils.config import config

service = get_image_generation_service()

# Configure from config object
gemini_config = config.get_gemini_config()
service.configure_gemini(gemini_config['api_key'])

storage_config = config.get_media_storage_config()
service.configure_storage(
    provider=StorageProvider.DIGITALOCEAN_SPACES,
    region=storage_config['region'],
    bucket=storage_config['bucket'],
    access_key=storage_config['access_key'],
    secret_key=storage_config['secret_key'],
    endpoint_url=storage_config['endpoint_url']
)
```

## Best Practices

### 1. Service Initialization

Initialize the service once at application startup:

```python
# app.py or __init__.py
from common.services.media import get_image_generation_service
from common.utils.config import config

def init_services():
    image_service = get_image_generation_service()
    image_service.configure_gemini(config.GEMINI_API_KEY)
    image_service.configure_storage(
        provider=StorageProvider.DIGITALOCEAN_SPACES,
        region=config.DIGITALOCEAN_SPACES_REGION,
        bucket=config.DIGITALOCEAN_SPACES_BUCKET,
        access_key=config.DIGITALOCEAN_SPACES_KEY,
        secret_key=config.DIGITALOCEAN_SPACES_SECRET
    )
```

### 2. Error Handling

Always wrap service calls in try-except:

```python
try:
    result = image_service.generate_and_upload(
        prompt=prompt,
        object_key=object_key
    )
except RuntimeError as e:
    logger.error(f"Service not configured: {e}")
except Exception as e:
    logger.error(f"Image generation failed: {e}")
```

### 3. Async Operations

Use Celery tasks for time-intensive operations:

```python
# Don't block the request
@app.route('/api/goals', methods=['POST'])
def create_goal():
    goal = create_goal_record(request.json)
    
    # Queue image generation
    generate_goal_image_task.delay(goal.id)
    
    return jsonify({"id": goal.id, "status": "pending"})
```

### 4. Object Key Naming

Use consistent, hierarchical naming:

```python
# Good
object_key = f"goals/{user_id}/{goal_id}/main.png"
object_key = f"portfolios/{user_id}/snapshot_{timestamp}.png"

# Avoid
object_key = "image123.png"
object_key = "goal_image.png"
```

### 5. Metadata Usage

Include useful metadata for debugging and tracking:

```python
metadata = {
    "user_id": str(user_id),
    "entity_type": "goal",
    "entity_id": str(goal_id),
    "generated_at": datetime.utcnow().isoformat(),
    "version": "1.0"
}
```

## Performance Considerations

### Image Generation Time

- **Low Quality**: 3-5 seconds
- **Medium Quality**: 5-8 seconds
- **High Quality**: 8-15 seconds

### Image Sizes

- **Thumbnail (256x256)**: ~50KB
- **Card (512x512)**: ~200KB
- **Standard (1024x1024)**: ~500KB-1MB
- **Banner (1920x1080)**: ~1-2MB

### Optimization Tips

1. Use appropriate size for use case
2. Use JPEG for photos, PNG for graphics
3. Enable CDN for frequently accessed images
4. Compress images appropriately
5. Cache generated images when possible

## Troubleshooting

### "Gemini API not configured"

```python
# Ensure API key is set
image_service.configure_gemini(config.GEMINI_API_KEY)
```

### "Storage not configured"

```python
# Ensure storage is configured
image_service.configure_storage(...)
```

### "No image found in response"

- Check Gemini API quota/limits
- Verify API key validity
- Check prompt clarity and length

### Upload Failures

- Verify storage credentials
- Check bucket permissions
- Ensure bucket exists
- Verify network connectivity

## Future Enhancements

- Video generation support
- Multiple AI model support (DALL-E, Stable Diffusion)
- Image editing capabilities
- Batch generation
- Template system
- A/B testing support
- Analytics integration

## Support

For issues or questions:
1. Check this documentation
2. Review configuration settings
3. Check application logs
4. Verify API credentials and quotas
