# timber/common/services/media/__init__.py
"""
Media Services

Provides AI-powered media generation and cloud storage services:
- Image generation using Google Gemini
- Video generation using Google Veo 3.1
- Cloud storage integration (DigitalOcean Spaces, AWS S3, GCS)
"""

from .image_generation import (
    ImageGenerationService,
    ImageGenerationConfig,
    ImageSize,
    ImageQuality,
    ImageTheme,
    get_image_generation_service,
)

from .video_generation import (
    VideoGenerationService,
    VideoGenerationConfig,
    VideoResolution,
    VideoDuration,
    VideoAspectRatio,
    VideoModel,
    VideoGenerationType,
    get_video_generation_service,
)

# Note: StorageProvider is defined in both modules but they're identical
from .image_generation import StorageProvider

__all__ = [
    # Image Services
    'ImageGenerationService',
    'get_image_generation_service',
    'ImageGenerationConfig',
    'ImageSize',
    'ImageQuality',
    'ImageTheme',
    
    # Video Services
    'VideoGenerationService',
    'get_video_generation_service',
    'VideoGenerationConfig',
    'VideoResolution',
    'VideoDuration',
    'VideoAspectRatio',
    'VideoModel',
    'VideoGenerationType',
    
    # Shared
    'StorageProvider',
]
