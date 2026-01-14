# Video Generation Service - Complete Guide

Comprehensive AI-powered video generation service using Google Veo 3.1 for the Timber ecosystem.

## Features

- **AI Video Generation**: Generate professional videos using Google Veo 3.1
- **Multiple Generation Modes**: Text-to-video, image-to-video, reference images, frame control, video extension
- **Cloud Storage**: Upload to DigitalOcean Spaces, AWS S3, or Google Cloud Storage
- **Native Audio**: Automatically generated synchronized audio and sound effects
- **Configurable**: Resolution (720p/1080p), duration (4/6/8s), aspect ratio (16:9/9:16)
- **Cinematic Control**: Specify camera movements, styles, and audio
- **Reference Images**: Use up to 3 images to guide character/style consistency
- **Video Extension**: Create longer videos by extending existing clips
- **Financial Application Optimized**: Defaults tuned for investment/financial platforms

## Installation

### Required Dependencies

```bash
pip install google-genai boto3 python-dotenv
```

### Environment Variables

Add to your `.env` file:

```bash
# Google Gemini API (with Veo access)
GEMINI_API_KEY=your_gemini_api_key_here

# Storage (DigitalOcean Spaces or AWS S3)
DIGITALOCEAN_SPACES_KEY=your_spaces_access_key
DIGITALOCEAN_SPACES_SECRET=your_spaces_secret_key
DIGITALOCEAN_SPACES_REGION=nyc3
DIGITALOCEAN_SPACES_BUCKET=your_bucket_name
```

**Important**: Veo 3.1 is in paid preview. You need a paid Gemini API tier with Veo access.

## Quick Start

### Basic Usage

```python
from common.services.media import get_video_generation_service, StorageProvider
from common.utils.config import config

# Get service instance
video_service = get_video_generation_service()

# Configure service (once at startup)
video_service.configure_gemini(config.GEMINI_API_KEY)
video_service.configure_storage(
    provider=StorageProvider.DIGITALOCEAN_SPACES,
    region=config.DIGITALOCEAN_SPACES_REGION,
    bucket=config.DIGITALOCEAN_SPACES_BUCKET,
    access_key=config.DIGITALOCEAN_SPACES_KEY,
    secret_key=config.DIGITALOCEAN_SPACES_SECRET
)

# Generate and upload video
result = video_service.generate_and_upload(
    prompt="A person achieving their retirement savings goal, celebrating success",
    object_key="videos/goals/retirement/user_123.mp4"
)

print(f"Video URL: {result['url']}")
print(f"Duration: {result['duration']} seconds")
print(f"Resolution: {result['resolution']}")
```

### Using Configuration

```python
from common.services.media import (
    VideoGenerationConfig,
    VideoResolution,
    VideoDuration,
    VideoAspectRatio,
    VideoModel
)

# Create custom configuration
config = VideoGenerationConfig(
    model=VideoModel.VEO_3_1,  # High quality
    resolution=VideoResolution.FULL_HD_1080P,
    duration=VideoDuration.STANDARD,  # 8 seconds
    aspect_ratio=VideoAspectRatio.LANDSCAPE,
    enable_audio=True,
    audio_description="Uplifting music with success sounds",
    cinematic_style="corporate, professional, inspiring"
)

# Generate with custom config
result = video_service.generate_and_upload(
    prompt="Portfolio growth visualization with rising charts",
    object_key="videos/portfolios/growth.mp4",
    config=config
)
```

## Configuration Options

### Video Models

```python
from common.services.media import VideoModel

VideoModel.VEO_3_1       # High quality (default)
VideoModel.VEO_3_1_FAST  # Faster generation, good quality
```

### Video Resolutions

```python
from common.services.media import VideoResolution

VideoResolution.HD_720P        # 1280x720 (default)
VideoResolution.FULL_HD_1080P  # 1920x1080 (requires 16:9)
```

### Video Durations

```python
from common.services.media import VideoDuration

VideoDuration.SHORT    # 4 seconds
VideoDuration.MEDIUM   # 6 seconds
VideoDuration.STANDARD # 8 seconds (default)
```

### Aspect Ratios

```python
from common.services.media import VideoAspectRatio

VideoAspectRatio.LANDSCAPE # 16:9 (default, supports 1080p)
VideoAspectRatio.PORTRAIT  # 9:16 (mobile/vertical)
VideoAspectRatio.AUTO      # Automatic
```

### Generation Types

```python
from common.services.media import VideoGenerationType

VideoGenerationType.TEXT_TO_VIDEO      # Text prompt only (default)
VideoGenerationType.IMAGE_TO_VIDEO     # Single image input
VideoGenerationType.REFERENCE_TO_VIDEO # 1-3 reference images
VideoGenerationType.FRAME_TO_FRAME     # First & last frame specified
VideoGenerationType.VIDEO_EXTENSION    # Extend existing video
```

## Advanced Usage

### Generate with Reference Images

```python
# Use 1-3 reference images for character/style consistency
config = VideoGenerationConfig(
    generation_type=VideoGenerationType.REFERENCE_TO_VIDEO,
    reference_images=[
        "https://example.com/character1.jpg",
        "https://example.com/character2.jpg",
        "https://example.com/style.jpg"
    ],
    duration=VideoDuration.STANDARD
)

result = video_service.generate_and_upload(
    prompt="The character walking through a modern office, looking confident",
    object_key="videos/character_scene.mp4",
    config=config
)
```

### Generate with First and Last Frame

```python
# Control exact start and end frames
config = VideoGenerationConfig(
    generation_type=VideoGenerationType.FRAME_TO_FRAME,
    first_frame="https://example.com/start_frame.jpg",
    last_frame="https://example.com/end_frame.jpg",
    duration=VideoDuration.STANDARD
)

result = video_service.generate_and_upload(
    prompt="Smooth transition with professional camera work",
    object_key="videos/transition.mp4",
    config=config
)
```

### Extend Existing Video

```python
# Create longer videos by extending clips
result = video_service.extend_video(
    video_url="https://your-bucket.com/videos/original.mp4",
    prompt="Continue the scene with the person walking into the office",
    object_key="videos/extended.mp4"
)
```

### Specify Camera Movements

```python
config = VideoGenerationConfig(
    camera_movements="Slow pan from left to right, gradual zoom on subject",
    cinematic_style="documentary, professional lighting",
    enable_audio=True,
    audio_description="Ambient office sounds with subtle music"
)

result = video_service.generate_and_upload(
    prompt="Professional office environment with people working",
    object_key="videos/office.mp4",
    config=config
)
```

### Portrait Video for Social Media

```python
# Generate vertical video for Instagram/TikTok
config = VideoGenerationConfig(
    aspect_ratio=VideoAspectRatio.PORTRAIT,  # 9:16
    duration=VideoDuration.MEDIUM,  # 6 seconds
    resolution=VideoResolution.HD_720P,  # Portrait doesn't support 1080p
    enable_audio=True,
    audio_description="Trendy upbeat music"
)

result = video_service.generate_and_upload(
    prompt="Quick financial tip visualization, modern and engaging",
    object_key="videos/social/tip_01.mp4",
    config=config
)
```

### Use Negative Prompt

```python
# Avoid specific content
config = VideoGenerationConfig(
    negative_prompt="text, logos, people's faces, specific brands"
)

result = video_service.generate_and_upload(
    prompt="Abstract visualization of investment growth",
    object_key="videos/abstract_growth.mp4",
    config=config
)
```

### Reproducible Results with Seed

```python
# Same seed = similar results
config = VideoGenerationConfig(
    seed=42  # Any integer
)

result = video_service.generate_and_upload(
    prompt="Financial success visualization",
    object_key="videos/success_v1.mp4",
    config=config
)
```

## Integration with Celery Tasks

### Example Task Implementation

```python
# tasks/video_generation_tasks.py
from celery import shared_task
from common.services.media import get_video_generation_service, VideoGenerationConfig
from your_app.models import UserGoal
from your_app.database import db

@shared_task(bind=True, max_retries=3)
def generate_goal_video_task(self, goal_id: int):
    """
    Celery task to generate video for a user goal.
    
    Note: Video generation takes 1-3 minutes, so this should be async.
    """
    try:
        # Get service (already configured at app startup)
        service = get_video_generation_service()
        
        # Get goal
        goal = UserGoal.query.get(goal_id)
        if not goal:
            raise Exception(f"Goal {goal_id} not found")
        
        # Update status
        goal.video_generation_status = 'generating'
        db.session.commit()
        
        # Configure for goal video
        config = VideoGenerationConfig(
            duration=VideoDuration.STANDARD,
            resolution=VideoResolution.FULL_HD_1080P,
            enable_audio=True,
            audio_description="Inspiring music with success sounds",
            cinematic_style="professional, motivational"
        )
        
        # Generate and upload
        result = service.generate_and_upload(
            prompt=f"Cinematic visualization of achieving {goal.name}, "
                   f"showing the journey and celebrating success",
            object_key=f"videos/goals/{goal.id}/{goal.name.replace(' ', '_').lower()}.mp4",
            config=config,
            metadata={
                "goal_id": str(goal.id),
                "user_id": str(goal.user_id),
                "goal_name": goal.name
            }
        )
        
        # Update goal
        goal.video_url = result['url']
        goal.video_prompt = result['prompt']
        goal.video_generation_status = 'completed'
        db.session.commit()
        
        return result['url']
        
    except Exception as e:
        if goal:
            goal.video_generation_status = 'failed'
            db.session.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=300)
```

## Performance Considerations

### Generation Times

- **Fast Model (VEO_3_1_FAST)**: 30-90 seconds
- **Quality Model (VEO_3_1)**: 1-3 minutes
- **With Reference Images**: +30-60 seconds
- **Extensions**: Similar to new generation

### Video Sizes

- **720p, 4 seconds**: ~2-5 MB
- **720p, 8 seconds**: ~5-10 MB
- **1080p, 4 seconds**: ~5-10 MB
- **1080p, 8 seconds**: ~10-20 MB

### Optimization Tips

1. Use VEO_3_1_FAST for quick previews
2. Use 720p for social media and drafts
3. Use 1080p only for final productions
4. Keep durations short (4-6s) for faster generation
5. Queue video generation as async tasks
6. Implement timeout handling (max 20 minutes)

## API Costs

Veo 3.1 is in **paid preview** (as of January 2025):

- Charged only on successful generation
- No charge for failed generations
- Pricing consistent with Veo 3.0
- Check Google Cloud Console for current rates

## Best Practices

### 1. Service Initialization

Initialize once at application startup:

```python
# app.py
from common.services.media import get_video_generation_service
from common.utils.config import config

def init_services():
    video_service = get_video_generation_service()
    video_service.configure_gemini(config.GEMINI_API_KEY)
    video_service.configure_storage(...)
```

### 2. Always Use Async

Video generation is slow (1-3 minutes). Always use Celery:

```python
# Good
generate_video_task.delay(goal_id=123)

# Bad (blocks request for minutes)
generate_video_task(goal_id=123)
```

### 3. Handle Timeouts

Videos can fail to generate. Implement proper error handling:

```python
config = VideoGenerationConfig(
    max_poll_attempts=120,  # 20 minutes max
    poll_interval=10  # Check every 10 seconds
)
```

### 4. Provide Clear Prompts

Veo works best with detailed, specific prompts:

```python
# Good
prompt = "Medium shot of a professional woman in her 30s reviewing financial charts " \
         "on a laptop in a modern office. Warm lighting, confident expression. " \
         "Camera slowly pushes in. Background: glass walls, plants."

# Less effective
prompt = "Person looking at charts"
```

### 5. Use Metadata

Track generation metadata for debugging:

```python
metadata = {
    "entity_type": "goal",
    "entity_id": str(goal_id),
    "user_id": str(user_id),
    "generated_at": datetime.utcnow().isoformat(),
    "model": config.model.value,
    "duration": str(config.duration.value)
}
```

## Troubleshooting

### "Gemini API not configured"
**Solution**: Call `configure_gemini()` after getting service instance.

### "Storage not configured"
**Solution**: Call `configure_storage()` after getting service instance.

### "Video generation timed out"
**Solution**: Increase `max_poll_attempts` or check API quota limits.

### "1080p resolution only available with 16:9 aspect ratio"
**Solution**: Use 720p for portrait (9:16) videos.

### "Reference generation requires at least 1 reference image"
**Solution**: Provide 1-3 reference images when using REFERENCE_TO_VIDEO mode.

### Videos not generating
**Possible causes:**
1. API quota exceeded - check Google Cloud Console
2. Invalid API key or no Veo access - verify in AI Studio
3. Network issues - check logs for connection errors
4. Invalid prompts - avoid prohibited content

## Watermarking

All Veo-generated videos include:
- **Visible watermark**: Added by Google
- **SynthID digital watermark**: Imperceptible identifier

These cannot be removed and indicate AI-generated content.

## Safety and Content Policy

Veo includes built-in safety filters:
- Blocks harmful/inappropriate requests
- Prevents copyright/privacy violations
- Filters biased outputs
- Moderates generated content

Videos are temporarily stored and deleted after 2 days unless downloaded.

## Comparison: Images vs Videos

| Feature | Image Service | Video Service |
|---------|--------------|---------------|
| Generation Time | 5-15 seconds | 1-3 minutes |
| File Size | 50KB-2MB | 2-20MB |
| Audio | No | Yes (synchronized) |
| Extension | No | Yes (up to 148s total) |
| Cost | Lower | Higher |
| Use Cases | Icons, thumbnails, hero images | Demos, education, marketing |

## Example Use Cases

### Financial Goal Achievement

```python
# 8-second video showing goal progress
config = VideoGenerationConfig(
    duration=VideoDuration.STANDARD,
    enable_audio=True,
    audio_description="Inspiring success music"
)

result = service.generate_and_upload(
    prompt="Journey toward retirement savings goal, showing discipline and celebration",
    object_key=f"videos/goals/{goal_id}/achievement.mp4",
    config=config
)
```

### Portfolio Performance Report

```python
# Professional performance visualization
config = VideoGenerationConfig(
    resolution=VideoResolution.FULL_HD_1080P,
    cinematic_style="corporate, data-driven, professional",
    camera_movements="Smooth pan across charts"
)

result = service.generate_and_upload(
    prompt="Portfolio performance with rising graphs and positive metrics",
    object_key=f"videos/portfolios/{portfolio_id}/report.mp4",
    config=config
)
```

### Educational Content

```python
# 6-second explainer video
config = VideoGenerationConfig(
    duration=VideoDuration.MEDIUM,
    enable_audio=True,
    audio_description="Clear narration with background music"
)

result = service.generate_and_upload(
    prompt="Simple explanation of compound interest with visual metaphors",
    object_key="videos/education/compound_interest.mp4",
    config=config
)
```

### Social Media Marketing

```python
# Vertical video for Instagram
config = VideoGenerationConfig(
    aspect_ratio=VideoAspectRatio.PORTRAIT,
    duration=VideoDuration.SHORT,
    model=VideoModel.VEO_3_1_FAST  # Faster for social
)

result = service.generate_and_upload(
    prompt="Quick investment tip, modern and engaging for mobile",
    object_key="videos/social/tip_daily.mp4",
    config=config
)
```

## Resources

- **Examples**: See `video_examples.py` for 13 practical patterns
- **API Documentation**: [Google Veo 3.1 Docs](https://ai.google.dev/gemini-api/docs/video)
- **Image Service**: See `README.md` for image generation
- **Configuration**: See `config_helpers.py` for integration

## Support

For issues or questions:
1. Check this documentation
2. Review configuration settings
3. Check application logs
4. Verify API credentials and quotas
5. Check Google Cloud Console for Veo access

---

**Created**: Production-ready video generation service using Veo 3.1
**Generation Time**: 1-3 minutes per video
**Resolutions**: 720p, 1080p (16:9 only)
**Durations**: 4, 6, 8 seconds (extensible to 148s)
**Audio**: Native synchronized audio generation
**Status**: Veo 3.1 in paid preview (January 2025)
