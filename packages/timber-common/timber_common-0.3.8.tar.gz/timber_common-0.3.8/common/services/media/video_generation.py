# timber/common/services/media/video_generation.py
"""
Video Generation Service

Generates AI videos using Google Veo 3.1 and uploads them to cloud storage.
Provides comprehensive configuration for duration, resolution, style, and audio.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Literal, List
from enum import Enum
from io import BytesIO
from dataclasses import dataclass, field

from google import genai as genaiClient
from google.genai import types

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class VideoResolution(str, Enum):
    """Video resolution presets"""
    HD_720P = "720p"       # 1280x720 (default)
    FULL_HD_1080P = "1080p"  # 1920x1080 (requires 16:9)


class VideoDuration(int, Enum):
    """Video duration options (in seconds)"""
    SHORT = 4       # 4 seconds
    MEDIUM = 6      # 6 seconds
    STANDARD = 8    # 8 seconds (default)


class VideoAspectRatio(str, Enum):
    """Video aspect ratio options"""
    LANDSCAPE = "16:9"   # Landscape (default) - supports 1080p
    PORTRAIT = "9:16"    # Portrait - mobile/vertical video
    AUTO = "auto"        # Automatic based on content


class VideoModel(str, Enum):
    """Veo model variants"""
    VEO_3_1 = "veo-3.1-generate-preview"          # High quality (default)
    VEO_3_1_FAST = "veo-3.1-fast-generate-preview"  # Faster generation


class VideoGenerationType(str, Enum):
    """Video generation modes"""
    TEXT_TO_VIDEO = "text_to_video"                    # Text prompt only
    IMAGE_TO_VIDEO = "image_to_video"                  # Single image input
    REFERENCE_TO_VIDEO = "reference_to_video"          # 1-3 reference images
    FRAME_TO_FRAME = "frame_to_frame"                  # First & last frame
    VIDEO_EXTENSION = "video_extension"                # Extend existing video


class StorageProvider(str, Enum):
    """Supported cloud storage providers"""
    DIGITALOCEAN_SPACES = "digitalocean_spaces"
    AWS_S3 = "aws_s3"
    GCS = "google_cloud_storage"
    LOCAL = "local"


@dataclass
class VideoGenerationConfig:
    """
    Configuration for video generation with sensible defaults for financial applications.
    
    Attributes:
        model: Veo model variant (quality vs speed)
        resolution: Video resolution (720p or 1080p)
        duration: Video length in seconds (4, 6, or 8)
        aspect_ratio: Video aspect ratio
        enable_audio: Whether to generate audio (default: True)
        audio_description: Description of desired audio/sound effects
        generation_type: Type of generation (text, image, reference, etc.)
        reference_images: List of reference image URLs/paths (1-3 for reference mode)
        first_frame: First frame image for frame-to-frame generation
        last_frame: Last frame image for frame-to-frame generation
        extend_from_video: Video to extend from
        negative_prompt: Content to avoid generating
        seed: Random seed for reproducibility
        cinematic_style: Specific cinematic style to apply
        camera_movements: Desired camera movements
        brand_colors: Brand colors to incorporate
        storage_provider: Where to upload videos
        storage_path_prefix: Prefix for storage path
        public_access: Whether videos should be publicly accessible
        cdn_enabled: Whether to use CDN for delivery
        max_poll_attempts: Maximum attempts to poll for completion
        poll_interval: Seconds between polling attempts
    """
    model: VideoModel = VideoModel.VEO_3_1
    resolution: VideoResolution = VideoResolution.HD_720P
    duration: VideoDuration = VideoDuration.STANDARD
    aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE
    enable_audio: bool = True
    audio_description: Optional[str] = None
    generation_type: VideoGenerationType = VideoGenerationType.TEXT_TO_VIDEO
    reference_images: List[str] = field(default_factory=list)
    first_frame: Optional[str] = None
    last_frame: Optional[str] = None
    extend_from_video: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    cinematic_style: Optional[str] = None
    camera_movements: Optional[str] = None
    brand_colors: List[str] = field(default_factory=lambda: ["#0066CC", "#00AA66"])
    storage_provider: StorageProvider = StorageProvider.DIGITALOCEAN_SPACES
    storage_path_prefix: str = "videos/"
    public_access: bool = True
    cdn_enabled: bool = False
    max_poll_attempts: int = 120  # 20 minutes max (10 sec intervals)
    poll_interval: int = 10  # seconds
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        # 1080p only available with 16:9
        if self.resolution == VideoResolution.FULL_HD_1080P:
            if self.aspect_ratio != VideoAspectRatio.LANDSCAPE:
                raise ValueError("1080p resolution only available with 16:9 aspect ratio")
        
        # Reference images validation
        if self.generation_type == VideoGenerationType.REFERENCE_TO_VIDEO:
            if not self.reference_images or len(self.reference_images) < 1:
                raise ValueError("Reference generation requires at least 1 reference image")
            if len(self.reference_images) > 3:
                raise ValueError("Maximum 3 reference images allowed")
        
        # Frame-to-frame validation
        if self.generation_type == VideoGenerationType.FRAME_TO_FRAME:
            if not self.first_frame:
                raise ValueError("Frame-to-frame requires first_frame")
        
        # Video extension validation
        if self.generation_type == VideoGenerationType.VIDEO_EXTENSION:
            if not self.extend_from_video:
                raise ValueError("Video extension requires extend_from_video")
    
    def get_resolution_dimensions(self) -> tuple[int, int]:
        """Get width and height for the configured resolution and aspect ratio"""
        if self.aspect_ratio == VideoAspectRatio.LANDSCAPE:
            if self.resolution == VideoResolution.FULL_HD_1080P:
                return (1920, 1080)
            else:
                return (1280, 720)
        elif self.aspect_ratio == VideoAspectRatio.PORTRAIT:
            if self.resolution == VideoResolution.FULL_HD_1080P:
                return (1080, 1920)  # Not officially supported
            else:
                return (720, 1280)
        return (1280, 720)  # Default


class VideoGenerationService:
    """
    Singleton service for AI video generation and cloud storage.
    
    Generates videos using Google Veo 3.1 and uploads to configured storage provider.
    Optimized for financial application use cases with professional defaults.
    """
    
    _instance: Optional['VideoGenerationService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoGenerationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._gemini_configured = False
        self._storage_client = None
        logger.info("Video Generation Service initialized")
    
    def configure_gemini(self, api_key: str) -> None:
        """
        Configure Google Gemini API for Veo access.
        
        Args:
            api_key: Google Gemini API key with Veo access
        """
        try:
            # Note: Veo uses the same Gemini API authentication
            os.environ['GOOGLE_API_KEY'] = api_key
            self._gemini_configured = True
            logger.info("Gemini API configured successfully for Veo")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise
    
    def configure_storage(
        self,
        provider: StorageProvider,
        region: str,
        bucket: str,
        access_key: str,
        secret_key: str,
        endpoint_url: Optional[str] = None
    ) -> None:
        """
        Configure cloud storage provider.
        
        Args:
            provider: Storage provider type
            region: Storage region
            bucket: Bucket/space name
            access_key: Access key ID
            secret_key: Secret access key
            endpoint_url: Custom endpoint URL (for DigitalOcean Spaces)
        """
        try:
            session = boto3.session.Session()
            
            if provider == StorageProvider.DIGITALOCEAN_SPACES:
                endpoint = endpoint_url or f'https://{region}.digitaloceanspaces.com'
            elif provider == StorageProvider.AWS_S3:
                endpoint = endpoint_url or f'https://s3.{region}.amazonaws.com'
            elif provider == StorageProvider.GCS:
                endpoint = endpoint_url or 'https://storage.googleapis.com'
            else:
                raise ValueError(f"Unsupported storage provider: {provider}")
            
            self._storage_client = session.client(
                's3',
                region_name=region,
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=BotoConfig(s3={'addressing_style': 'virtual'}),
            )
            
            self._storage_config = {
                'provider': provider,
                'region': region,
                'bucket': bucket,
                'endpoint_url': endpoint
            }
            
            logger.info(f"Storage configured: {provider.value} in {region}")
        except Exception as e:
            logger.error(f"Failed to configure storage: {e}")
            raise
    
    def _build_prompt(
        self,
        base_prompt: str,
        config: VideoGenerationConfig,
        enhance_for_finance: bool = True
    ) -> str:
        """
        Build enhanced prompt with configuration parameters.
        
        Args:
            base_prompt: User's base prompt describing what to generate
            config: Video generation configuration
            enhance_for_finance: Add financial application enhancements
            
        Returns:
            Enhanced prompt string
        """
        prompt_parts = [base_prompt]
        
        # Add cinematic style
        if config.cinematic_style:
            prompt_parts.append(f"Cinematic style: {config.cinematic_style}.")
        
        # Add camera movements
        if config.camera_movements:
            prompt_parts.append(f"Camera movements: {config.camera_movements}.")
        
        # Add audio description
        if config.enable_audio and config.audio_description:
            prompt_parts.append(f"Audio: {config.audio_description}.")
        
        # Add brand colors if specified
        if config.brand_colors:
            colors_text = ", ".join(config.brand_colors)
            prompt_parts.append(
                f"Incorporate these brand colors where appropriate: {colors_text}."
            )
        
        # Add financial context enhancements
        if enhance_for_finance:
            prompt_parts.append(
                "The video should evoke financial success, professionalism, and trust. "
                "It should be polished, inspiring, and suitable for a financial "
                "investment platform."
            )
        
        return " ".join(prompt_parts)
    
    def generate_video(
        self,
        prompt: str,
        config: Optional[VideoGenerationConfig] = None,
        enhance_for_finance: bool = True,
        save_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a video using Google Veo 3.1.
        
        Args:
            prompt: Description of the video to generate
            config: Configuration options (uses defaults if not provided)
            enhance_for_finance: Add financial application enhancements to prompt
            save_prompt: Whether to return the full prompt used
            
        Returns:
            Dictionary containing:
                - video_bytes: Video file bytes
                - format: Video format (mp4)
                - prompt: Full prompt used (if save_prompt=True)
                - duration: Video duration in seconds
                - resolution: Video resolution
                - operation_name: Operation name for tracking
                
        Raises:
            RuntimeError: If Gemini is not configured
            Exception: If generation fails
        """
        if not self._gemini_configured:
            raise RuntimeError("Gemini API not configured. Call configure_gemini() first.")
        
        config = config or VideoGenerationConfig()
        config.validate()
        
        # Build enhanced prompt
        full_prompt = self._build_prompt(prompt, config, enhance_for_finance)
        logger.info(f"Generating video with prompt: {full_prompt[:100]}...")
        
        try:
            client = genaiClient.Client()
            
            # Prepare generation config
            generation_config = types.GenerateVideosConfig(
                aspect_ratio=config.aspect_ratio.value if config.aspect_ratio != VideoAspectRatio.AUTO else None,
                resolution=config.resolution.value,
                duration=config.duration.value,
            )
            
            # Add optional parameters
            if config.seed is not None:
                generation_config.seed = config.seed
            
            if config.negative_prompt:
                generation_config.negative_prompt = config.negative_prompt
            
            # Prepare inputs based on generation type
            kwargs = {
                'model': config.model.value,
                'prompt': full_prompt,
                'config': generation_config
            }
            
            # Add reference images if specified
            if config.reference_images:
                kwargs['config'].reference_images = config.reference_images
            
            # Add frame parameters
            if config.first_frame:
                # Read first frame
                kwargs['image'] = config.first_frame
                if config.last_frame:
                    kwargs['config'].last_frame = config.last_frame
            
            # Generate video (async operation)
            logger.info(f"Starting video generation with model {config.model.value}")
            operation = client.models.generate_videos(**kwargs)
            
            # Poll for completion
            attempts = 0
            while not operation.done and attempts < config.max_poll_attempts:
                logger.info(f"Waiting for video generation... (attempt {attempts + 1}/{config.max_poll_attempts})")
                time.sleep(config.poll_interval)
                operation = client.operations.get_videos_operation(operation.name)
                attempts += 1
            
            if not operation.done:
                raise Exception(f"Video generation timed out after {config.max_poll_attempts * config.poll_interval} seconds")
            
            if not operation.response or not operation.response.generated_videos:
                raise Exception("No video generated in response")
            
            # Get generated video
            generated_video = operation.response.generated_videos[0]
            
            # Download video bytes
            video_file = client.files.get(generated_video.video.name)
            video_bytes = video_file.read()
            
            logger.info(f"Video generated successfully: {len(video_bytes)} bytes")
            
            result = {
                'video_bytes': video_bytes,
                'format': 'mp4',
                'duration': config.duration.value,
                'resolution': config.resolution.value,
                'operation_name': operation.name,
            }
            
            if save_prompt:
                result['prompt'] = full_prompt
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate video: {e}", exc_info=True)
            raise
    
    def upload_video(
        self,
        video_bytes: bytes,
        object_key: str,
        config: Optional[VideoGenerationConfig] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload video to configured cloud storage.
        
        Args:
            video_bytes: Video file bytes to upload
            object_key: Storage path/key for the video
            config: Configuration for storage options
            metadata: Optional metadata to attach to the object
            
        Returns:
            Public URL to the uploaded video
            
        Raises:
            RuntimeError: If storage is not configured
            ClientError: If upload fails
        """
        if not self._storage_client:
            raise RuntimeError("Storage not configured. Call configure_storage() first.")
        
        config = config or VideoGenerationConfig()
        
        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self._storage_config['bucket'],
                'Key': object_key,
                'Body': video_bytes,
                'ContentType': 'video/mp4',
            }
            
            # Add public access if configured
            if config.public_access:
                upload_params['ACL'] = 'public-read'
            
            # Add metadata if provided
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Upload to storage
            logger.info(f"Uploading video to {object_key} ({len(video_bytes)} bytes)")
            self._storage_client.put_object(**upload_params)
            
            # Build public URL
            bucket = self._storage_config['bucket']
            region = self._storage_config['region']
            provider = self._storage_config['provider']
            
            if provider == StorageProvider.DIGITALOCEAN_SPACES:
                if config.cdn_enabled:
                    video_url = f"https://{bucket}.{region}.cdn.digitaloceanspaces.com/{object_key}"
                else:
                    video_url = f"https://{bucket}.{region}.digitaloceanspaces.com/{object_key}"
            elif provider == StorageProvider.AWS_S3:
                if config.cdn_enabled:
                    logger.warning("CDN URL requested but CloudFront domain not configured")
                video_url = f"https://{bucket}.s3.{region}.amazonaws.com/{object_key}"
            else:
                video_url = f"{self._storage_config['endpoint_url']}/{bucket}/{object_key}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            return video_url
            
        except ClientError as e:
            logger.error(f"Failed to upload video: {e}", exc_info=True)
            raise
    
    def generate_and_upload(
        self,
        prompt: str,
        object_key: str,
        config: Optional[VideoGenerationConfig] = None,
        enhance_for_finance: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a video and upload it to storage in one operation.
        
        Args:
            prompt: Description of the video to generate
            object_key: Storage path/key for the video
            config: Configuration options
            enhance_for_finance: Add financial application enhancements
            metadata: Optional metadata to attach to the object
            
        Returns:
            Dictionary containing:
                - url: Public URL to the uploaded video
                - prompt: Full prompt used
                - duration: Video duration
                - resolution: Video resolution
                - format: Video format
                - operation_name: Generation operation name
                
        Raises:
            RuntimeError: If Gemini or storage not configured
            Exception: If generation or upload fails
        """
        config = config or VideoGenerationConfig()
        
        # Generate video
        generation_result = self.generate_video(
            prompt=prompt,
            config=config,
            enhance_for_finance=enhance_for_finance,
            save_prompt=True
        )
        
        # Add metadata about generation
        gen_metadata = metadata or {}
        gen_metadata.update({
            'generated_by': config.model.value,
            'duration': str(generation_result['duration']),
            'resolution': generation_result['resolution'],
            'operation': generation_result['operation_name'],
        })
        
        # Upload video
        video_url = self.upload_video(
            video_bytes=generation_result['video_bytes'],
            object_key=object_key,
            config=config,
            metadata=gen_metadata
        )
        
        return {
            'url': video_url,
            'prompt': generation_result['prompt'],
            'duration': generation_result['duration'],
            'resolution': generation_result['resolution'],
            'format': 'mp4',
            'operation_name': generation_result['operation_name'],
        }
    
    def extend_video(
        self,
        video_url: str,
        prompt: Optional[str] = None,
        object_key: str = None,
        config: Optional[VideoGenerationConfig] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Extend an existing video by generating a continuation.
        
        Args:
            video_url: URL to the video to extend
            prompt: Optional prompt to guide the extension
            object_key: Storage path for the extended video
            config: Configuration options
            metadata: Optional metadata
            
        Returns:
            Dictionary with extended video URL and metadata
        """
        config = config or VideoGenerationConfig()
        config.generation_type = VideoGenerationType.VIDEO_EXTENSION
        config.extend_from_video = video_url
        
        prompt = prompt or "Continue the video seamlessly"
        
        return self.generate_and_upload(
            prompt=prompt,
            object_key=object_key,
            config=config,
            enhance_for_finance=False,
            metadata=metadata
        )
    
    def delete_video(self, object_key: str) -> bool:
        """
        Delete a video from storage.
        
        Args:
            object_key: Storage path/key of the video to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self._storage_client:
            raise RuntimeError("Storage not configured. Call configure_storage() first.")
        
        try:
            self._storage_client.delete_object(
                Bucket=self._storage_config['bucket'],
                Key=object_key
            )
            logger.info(f"Deleted video: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete video {object_key}: {e}")
            return False


# Singleton instance getter
def get_video_generation_service() -> VideoGenerationService:
    """Get the singleton VideoGenerationService instance"""
    return VideoGenerationService()
