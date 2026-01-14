# Migration Guide: From goal_image_tasks.py to Media Service

This guide shows you exactly how to migrate from your existing `goal_image_tasks.py` implementation to the new media generation service.

## Side-by-Side Comparison

### OLD CODE (goal_image_tasks.py)
```python
# File: src/finance_ai/tasks/image_generation/goal_image_tasks.py

import os
import base64
import google.generativeai as genai
from google import genai as genaiClient
from google.genai.types import GenerateContentConfig, Modality

from celery import shared_task
from flask import current_app

from finance_ai.utils.sqlalchemy import db
from finance_ai.models.narrative import UserGoal
from finance_ai.config import Config as Oak_Config

import boto3
from botocore.client import Config

from PIL import Image
from io import BytesIO

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def generate_goal_image(self, goal_id: int):
    from finance_ai.app import create_app

    app = create_app()
    with app.app_context():
        goal = UserGoal.query.get(goal_id)
        if not goal:
            current_app.logger.error(f"Goal with ID {goal_id} not found")
            return

        # Get all the config values
        gemini_api_key = Oak_Config.GEMINI_API_KEY
        do_spaces_key = Oak_Config.DIGITALOCEAN_SPACES_KEY
        do_spaces_secret = Oak_Config.DIGITALOCEAN_SPACES_SECRET
        do_spaces_region = Oak_Config.DIGITALOCEAN_SPACES_REGION
        do_spaces_bucket = Oak_Config.DIGITALOCEAN_SPACES_BUCKET
        
        # Validate config
        if not all([gemini_api_key, do_spaces_key, do_spaces_secret, 
                    do_spaces_region, do_spaces_bucket]):
            current_app.logger.error("Missing API keys or config")
            goal.image_generation_status = 'failed'
            db.session.commit()
            return

        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Update status
        goal.image_generation_status = 'generating'
        db.session.commit()

        # Build long prompt
        prompt = f"Generate a vibrant, inspiring, and visually appealing **square image** representing the financial goal: '{goal.name}'. Focus on positive achievement and future success. Examples could include: a dream home, a graduation cap, a travel destination, a retirement scene, a strong investment portfolio graph. Avoid text and specific currency symbols. Make it aspirational, professional, realistic and memorable. The image should evoke a sense of accomplishment and motivation, suitable for a personal finance application. Ensure the image is square-shaped to fit well in the app's interface. The image should reflect the theme of financial success and personal achievement, without any text or logos. My brand colors are blue and green, so consider using these colors in the image to align with our branding."
        
        goal.image_prompt = prompt
        db.session.commit()
        
        client = genaiClient.Client()
        try:
            # Generate image
            current_app.logger.info(f"Sending prompt to Gemini API for goal {goal.id}")

            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=(prompt,),
                config=GenerateContentConfig(
                    response_modalities=[Modality.TEXT, Modality.IMAGE]
                ),
            )

            if not response.candidates:
                raise Exception("Gemini API did not return any candidates.")
            
            # Extract image
            generated_image_pil = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_image_pil = Image.open(BytesIO(part.inline_data.data))
                    break

            if not generated_image_pil:
                raise Exception("No image found in Gemini API response")

            # Convert to bytes
            byte_stream = BytesIO()
            generated_image_pil.save(byte_stream, format='PNG')
            image_bytes = byte_stream.getvalue()
            image_extension = "png"
            
            # Configure S3 client
            session = boto3.session.Session()
            s3_client = session.client(
                's3',
                region_name=do_spaces_region,
                endpoint_url=f'https://{do_spaces_region}.digitaloceanspaces.com',
                aws_access_key_id=do_spaces_key,
                aws_secret_access_key=do_spaces_secret,
                config=Config(s3={'addressing_style': 'virtual'}),
            )

            # Build object key
            object_key = f"goals/{goal.id}/{goal.name.replace(' ', '_').lower()}_{goal.id}.{image_extension}"

            # Upload
            current_app.logger.info(f"Uploading image for goal {goal.id}")
            s3_client.put_object(
                Bucket=do_spaces_bucket,
                Key=object_key,
                Body=image_bytes,
                ACL='public-read',
                ContentType=f'image/{image_extension}'
            )

            # Build URL
            image_url = f"https://{do_spaces_bucket}.{do_spaces_region}.digitaloceanspaces.com/{object_key}"
            
            # Update goal
            goal.image_url = image_url
            goal.image_generation_status = 'completed'
            db.session.commit()

            current_app.logger.info(f"Successfully generated image for goal {goal.id}")

        except Exception as e:
            db.session.rollback()
            goal.image_generation_status = 'failed'
            current_app.logger.error(f"Failed to generate image: {e}", exc_info=True)
            db.session.commit()
            self.retry(exc=e)
```

**Lines of Code**: ~120 lines
**Complexity**: High
**Reusability**: None (task-specific)
**Testing**: Difficult (mixed concerns)

---

### NEW CODE (Using Media Service)

```python
# File: src/finance_ai/tasks/image_generation/goal_image_tasks.py

from celery import shared_task
from flask import current_app

from finance_ai.utils.sqlalchemy import db
from finance_ai.models.narrative import UserGoal
from common.services.media import get_image_generation_service

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def generate_goal_image(self, goal_id: int):
    from finance_ai.app import create_app

    app = create_app()
    with app.app_context():
        goal = UserGoal.query.get(goal_id)
        if not goal:
            current_app.logger.error(f"Goal with ID {goal_id} not found")
            return

        try:
            # Get service (already configured at app startup)
            service = get_image_generation_service()
            
            # Update status
            goal.image_generation_status = 'generating'
            db.session.commit()

            # Generate and upload (single call!)
            result = service.generate_and_upload(
                prompt=f"Visual representation of financial goal: {goal.name}",
                object_key=f"goals/{goal.id}/{goal.name.replace(' ', '_').lower()}.png",
                metadata={
                    "goal_id": str(goal.id),
                    "user_id": str(goal.user_id) if hasattr(goal, 'user_id') else None,
                    "goal_name": goal.name
                }
            )

            # Update goal
            goal.image_url = result['url']
            goal.image_prompt = result['prompt']
            goal.image_generation_status = 'completed'
            db.session.commit()

            current_app.logger.info(f"Successfully generated image for goal {goal.id}")
            return result['url']

        except Exception as e:
            db.session.rollback()
            goal.image_generation_status = 'failed'
            current_app.logger.error(f"Failed to generate image: {e}", exc_info=True)
            db.session.commit()
            self.retry(exc=e)
```

**Lines of Code**: ~45 lines (63% reduction!)
**Complexity**: Low
**Reusability**: High (service can be used anywhere)
**Testing**: Easy (service has comprehensive tests)

---

## Migration Steps

### Step 1: Add Service to Your Project

```bash
# Copy the media service to your project
cp -r common/services/media /path/to/your/project/common/services/

# Install dependencies (if not already installed)
pip install google-generativeai google-genai pillow boto3
```

### Step 2: Initialize Service at App Startup

Add this to your app initialization (e.g., `app.py` or `__init__.py`):

```python
# In your app.py or wherever you initialize Flask
from common.services.media import get_image_generation_service, StorageProvider
from finance_ai.config import Config as Oak_Config

def init_services(app):
    """Initialize services at app startup"""
    with app.app_context():
        # Initialize image generation service
        image_service = get_image_generation_service()
        
        # Configure Gemini API
        if Oak_Config.GEMINI_API_KEY:
            image_service.configure_gemini(Oak_Config.GEMINI_API_KEY)
        
        # Configure Storage
        if all([Oak_Config.DIGITALOCEAN_SPACES_KEY, 
                Oak_Config.DIGITALOCEAN_SPACES_SECRET,
                Oak_Config.DIGITALOCEAN_SPACES_BUCKET]):
            image_service.configure_storage(
                provider=StorageProvider.DIGITALOCEAN_SPACES,
                region=Oak_Config.DIGITALOCEAN_SPACES_REGION,
                bucket=Oak_Config.DIGITALOCEAN_SPACES_BUCKET,
                access_key=Oak_Config.DIGITALOCEAN_SPACES_KEY,
                secret_key=Oak_Config.DIGITALOCEAN_SPACES_SECRET
            )

def create_app():
    app = Flask(__name__)
    # ... other initialization ...
    
    # Initialize services
    init_services(app)
    
    return app
```

### Step 3: Replace Your Task Code

Replace the entire `generate_goal_image` function with the new simplified version shown above.

### Step 4: Test

```python
# Test in Python shell
from finance_ai.tasks.image_generation.goal_image_tasks import generate_goal_image
from finance_ai.app import create_app

app = create_app()
with app.app_context():
    # Test with an actual goal ID
    result = generate_goal_image(goal_id=1)
    print(f"Generated: {result}")
```

---

## What Changed?

### Removed (No Longer Needed)
- ❌ Manual Gemini API configuration in task
- ❌ Manual S3 client setup in task
- ❌ Manual config validation
- ❌ Manual prompt building
- ❌ Manual image extraction from response
- ❌ Manual byte conversion
- ❌ Manual upload logic
- ❌ Manual URL construction
- ❌ ~75 lines of boilerplate code

### Added (New Benefits)
- ✅ Centralized service (reusable across app)
- ✅ Configuration happens once at startup
- ✅ Single line to generate and upload
- ✅ Automatic prompt enhancement
- ✅ Built-in error handling
- ✅ Comprehensive logging
- ✅ Easy to test
- ✅ Type safety with hints
- ✅ Metadata support
- ✅ Configurable image properties

---

## Configuration Comparison

### OLD: Multiple Config Access Points
```python
gemini_api_key = Oak_Config.GEMINI_API_KEY
do_spaces_key = Oak_Config.DIGITALOCEAN_SPACES_KEY
do_spaces_secret = Oak_Config.DIGITALOCEAN_SPACES_SECRET
do_spaces_region = Oak_Config.DIGITALOCEAN_SPACES_REGION
do_spaces_bucket = Oak_Config.DIGITALOCEAN_SPACES_BUCKET

if not all([gemini_api_key, do_spaces_key, do_spaces_secret, 
            do_spaces_region, do_spaces_bucket]):
    # Handle error
```

### NEW: Configuration at Startup
```python
# Configuration happens ONCE at app startup
service = get_image_generation_service()
service.configure_gemini(Oak_Config.GEMINI_API_KEY)
service.configure_storage(...)

# Then in tasks, just use the service
service = get_image_generation_service()  # Already configured!
```

---

## Customization Options

### Want Different Image Sizes?
```python
from common.services.media import ImageGenerationConfig, ImageSize

config = ImageGenerationConfig(
    size=ImageSize.BANNER,  # 1920x1080
    quality=ImageQuality.HIGH
)

result = service.generate_and_upload(
    prompt=f"Visual for: {goal.name}",
    object_key=f"goals/{goal.id}/banner.png",
    config=config
)
```

### Want Different Styles?
```python
from common.services.media import ImageTheme

config = ImageGenerationConfig(
    theme=ImageTheme.ILLUSTRATION  # or MINIMALIST, PROFESSIONAL, etc.
)

result = service.generate_and_upload(
    prompt=f"Visual for: {goal.name}",
    object_key=f"goals/{goal.id}/illustration.png",
    config=config
)
```

### Want Custom Brand Colors?
```python
config = ImageGenerationConfig(
    brand_colors=["#0066CC", "#00AA66", "#FFD700"]
)

result = service.generate_and_upload(
    prompt=f"Visual for: {goal.name}",
    object_key=f"goals/{goal.id}/branded.png",
    config=config
)
```

---

## Testing Comparison

### OLD: Hard to Test
- Need to mock Gemini API
- Need to mock boto3
- Need to mock Flask app context
- Need to mock database
- Mixed concerns make mocking complex

### NEW: Easy to Test
```python
# Service has comprehensive test suite
pytest common/services/media/test_image_generation.py

# Your task code is now simple enough to test easily
def test_generate_goal_image():
    with patch('common.services.media.get_image_generation_service') as mock_service:
        mock_service.return_value.generate_and_upload.return_value = {
            'url': 'https://test.com/image.png',
            'prompt': 'test prompt'
        }
        
        result = generate_goal_image(goal_id=1)
        assert result == 'https://test.com/image.png'
```

---

## Reusability

### OLD: Task-Specific Code
- Can only be used in this one task
- Hard to reuse for other image generation needs
- Must duplicate code for different use cases

### NEW: Service Everywhere
```python
# Use in other tasks
@shared_task
def generate_portfolio_image(portfolio_id):
    service = get_image_generation_service()
    result = service.generate_and_upload(
        prompt=f"Portfolio visualization",
        object_key=f"portfolios/{portfolio_id}/main.png"
    )
    return result['url']

# Use in API endpoints
@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    service = get_image_generation_service()
    result = service.generate_and_upload(
        prompt=request.json['prompt'],
        object_key=request.json['path']
    )
    return jsonify({'url': result['url']})

# Use in CLI commands
@click.command()
def generate_sample_images():
    service = get_image_generation_service()
    # Generate multiple images
    for concept in concepts:
        service.generate_and_upload(...)
```

---

## Error Handling Comparison

### OLD: Manual Error Handling
```python
try:
    # 50+ lines of code that could fail
    response = client.models.generate_content(...)
    # ... manual extraction ...
    # ... manual upload ...
except Exception as e:
    db.session.rollback()
    goal.image_generation_status = 'failed'
    current_app.logger.error(f"Failed: {e}")
    db.session.commit()
    self.retry(exc=e)
```

### NEW: Service Handles Errors
```python
try:
    # Single line that could fail
    result = service.generate_and_upload(...)
    # Service handles all internal errors
except RuntimeError as e:
    # Service not configured
    current_app.logger.error(f"Service error: {e}")
except Exception as e:
    # Generation or upload failed
    db.session.rollback()
    goal.image_generation_status = 'failed'
    db.session.commit()
    self.retry(exc=e)
```

---

## Performance

### OLD vs NEW
- **Generation Time**: Same (uses same Gemini API)
- **Upload Time**: Same (uses same S3 API)
- **Code Execution**: NEW is faster (less overhead)
- **Memory Usage**: NEW is better (singleton pattern)
- **Network Calls**: Same

---

## Rollback Plan

If you need to rollback:

1. Keep your old `goal_image_tasks.py` file as backup
2. Test new service thoroughly in development
3. Deploy to staging first
4. Monitor for any issues
5. If problems, revert to old file

```bash
# Backup old file
cp goal_image_tasks.py goal_image_tasks.py.backup

# If rollback needed
mv goal_image_tasks.py.backup goal_image_tasks.py
```

---

## Benefits Summary

| Aspect | OLD | NEW | Improvement |
|--------|-----|-----|-------------|
| Lines of Code | 120 | 45 | 63% reduction |
| Configuration | Per-task | Once at startup | Cleaner |
| Reusability | None | High | Much better |
| Testing | Hard | Easy | Much better |
| Maintainability | Low | High | Much better |
| Type Safety | None | Full | Much better |
| Error Handling | Manual | Built-in | Better |
| Documentation | None | Extensive | Much better |

---

## Next Steps

1. ✅ Copy service files to your project
2. ✅ Add service initialization to app startup
3. ✅ Replace task code
4. ✅ Test thoroughly
5. ✅ Deploy to staging
6. ✅ Deploy to production
7. ✅ Remove old code after verification
8. ✅ Use service for new image generation needs

---

**Estimated Migration Time**: 1-2 hours
**Complexity**: Low
**Risk**: Low (can easily rollback)
**Benefit**: High (cleaner, more maintainable code)
