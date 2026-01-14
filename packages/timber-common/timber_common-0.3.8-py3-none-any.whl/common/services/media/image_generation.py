# timber/common/services/media/image_generation.py
"""
Image Generation Service

Generates AI images using Google Gemini and uploads them to cloud storage (DigitalOcean Spaces/S3).
Provides comprehensive configuration for size, quality, style, and storage options.
"""

import os
import logging
from typing import Optional, Dict, Any, Literal
from enum import Enum
from io import BytesIO
from dataclasses import dataclass, field
from PIL import Image

from google import genai
from google import genai as genaiClient
from google.genai.types import GenerateContentConfig, Modality

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ImageSize(str, Enum):
    """Standard image size presets for financial applications"""
    THUMBNAIL = "256x256"      # Small thumbnails for lists
    CARD = "512x512"          # Card displays
    STANDARD = "1024x1024"    # Standard square images (default)
    BANNER = "1920x1080"      # Banner/hero images
    WIDE_CARD = "1280x720"    # Wide card format
    PORTRAIT = "768x1024"     # Portrait orientation
    CUSTOM = "custom"          # Custom dimensions


class ImageQuality(str, Enum):
    """Image quality/compression settings"""
    LOW = "low"          # Faster generation, smaller files
    MEDIUM = "medium"    # Balanced (default)
    HIGH = "high"        # Best quality, larger files


class ImageTheme(str, Enum):
    """Visual style themes for generated images"""
    REALISTIC = "realistic"                    # Photo-realistic (default)
    ILLUSTRATION = "illustration"              # Illustrated style
    ABSTRACT = "abstract"                      # Abstract/conceptual
    MINIMALIST = "minimalist"                  # Clean, minimal design
    PROFESSIONAL = "professional"              # Corporate/professional
    FUTURISTIC = "futuristic"                 # Modern/tech aesthetic
    INFOGRAPHIC = "infographic"               # Data visualization style
    VINTAGE = "vintage"                        # Classic/retro style


class StorageProvider(str, Enum):
    """Supported cloud storage providers"""
    DIGITALOCEAN_SPACES = "digitalocean_spaces"
    AWS_S3 = "aws_s3"
    LOCAL = "local"  # For testing/development


@dataclass
class ImageGenerationConfig:
    """
    Configuration for image generation with sensible defaults for financial applications.
    
    Attributes:
        size: Image dimensions (default: 1024x1024 square)
        quality: Image quality level (default: medium)
        theme: Visual style theme (default: realistic)
        custom_width: Custom width if size is CUSTOM
        custom_height: Custom height if size is CUSTOM
        format: Output format (png, jpeg, webp)
        brand_colors: List of brand colors to incorporate (hex codes)
        avoid_text: Whether to avoid text in images (default: True)
        avoid_symbols: Whether to avoid currency symbols (default: True)
        aspect_ratio: Aspect ratio preference (1:1, 16:9, 4:3, etc.)
        storage_provider: Where to upload images
        storage_path_prefix: Prefix for storage path (e.g., "images/goals/")
        public_access: Whether images should be publicly accessible
        cdn_enabled: Whether to use CDN for image delivery
        compression_level: PNG compression level (0-9)
        jpeg_quality: JPEG quality (1-100)
    """
    size: ImageSize = ImageSize.STANDARD
    quality: ImageQuality = ImageQuality.MEDIUM
    theme: ImageTheme = ImageTheme.REALISTIC
    custom_width: Optional[int] = None
    custom_height: Optional[int] = None
    format: Literal["png", "jpeg", "webp"] = "png"
    brand_colors: list[str] = field(default_factory=lambda: ["#0066CC", "#00AA66"])  # Blue and green
    avoid_text: bool = True
    avoid_symbols: bool = True
    aspect_ratio: Optional[str] = None
    storage_provider: StorageProvider = StorageProvider.DIGITALOCEAN_SPACES
    storage_path_prefix: str = "images/"
    public_access: bool = True
    cdn_enabled: bool = False
    compression_level: int = 6  # PNG compression (0-9)
    jpeg_quality: int = 85  # JPEG quality (1-100)
    
    def get_dimensions(self) -> tuple[Optional[int], Optional[int]]:
        """Get width and height for the configured size"""
        if self.size == ImageSize.CUSTOM:
            return (self.custom_width, self.custom_height)
        
        dimension_map = {
            ImageSize.THUMBNAIL: (256, 256),
            ImageSize.CARD: (512, 512),
            ImageSize.STANDARD: (1024, 1024),
            ImageSize.BANNER: (1920, 1080),
            ImageSize.WIDE_CARD: (1280, 720),
            ImageSize.PORTRAIT: (768, 1024),
        }
        return dimension_map.get(self.size, (1024, 1024))
    
    def get_theme_description(self) -> str:
        """Get descriptive text for the theme to include in prompts"""
        theme_descriptions = {
            ImageTheme.REALISTIC: "photo-realistic, natural, authentic",
            ImageTheme.ILLUSTRATION: "illustrated, hand-drawn aesthetic, artistic",
            ImageTheme.ABSTRACT: "abstract, conceptual, symbolic",
            ImageTheme.MINIMALIST: "minimalist, clean lines, simple, uncluttered",
            ImageTheme.PROFESSIONAL: "professional, corporate, polished, business-appropriate",
            ImageTheme.FUTURISTIC: "futuristic, modern, technological, innovative",
            ImageTheme.INFOGRAPHIC: "infographic-style, data visualization, clean graphics",
            ImageTheme.VINTAGE: "vintage, classic, timeless, retro-inspired",
        }
        return theme_descriptions.get(self.theme, "professional and polished")


class ImageGenerationService:
    """
    Singleton service for AI image generation and cloud storage.
    
    Generates images using Google Gemini and uploads to configured storage provider.
    Optimized for financial application use cases with professional defaults.
    """
    
    _instance: Optional['ImageGenerationService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageGenerationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._gemini_configured = False
        self._storage_client = None
        logger.info("Image Generation Service initialized")
    
    def configure_gemini(self, api_key: str) -> None:
        """
        Configure Google Gemini API.
        
        Args:
            api_key: Google Gemini API key
        """
        try:
            genai.configure(api_key=api_key)
            self._gemini_configured = True
            logger.info("Gemini API configured successfully")
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
        config: ImageGenerationConfig,
        enhance_for_finance: bool = True
    ) -> str:
        """
        Build enhanced prompt with configuration parameters.
        
        Args:
            base_prompt: User's base prompt describing what to generate
            config: Image generation configuration
            enhance_for_finance: Add financial application enhancements
            
        Returns:
            Enhanced prompt string
        """
        prompt_parts = [base_prompt]
        
        # Add size/aspect ratio guidance
        width, height = config.get_dimensions()
        if width and height:
            if width == height:
                prompt_parts.append("Create a square-shaped image.")
            else:
                prompt_parts.append(f"Create an image with {width}x{height} dimensions.")
        
        # Add theme/style guidance
        theme_desc = config.get_theme_description()
        prompt_parts.append(f"Style: {theme_desc}.")
        
        # Add brand colors if specified
        if config.brand_colors:
            colors_text = ", ".join(config.brand_colors)
            prompt_parts.append(
                f"Incorporate these brand colors where appropriate: {colors_text}."
            )
        
        # Add financial context enhancements
        if enhance_for_finance:
            prompt_parts.append(
                "The image should evoke financial success, achievement, and trust. "
                "It should be professional, inspiring, and suitable for a financial "
                "investment platform."
            )
        
        # Add constraints
        constraints = []
        if config.avoid_text:
            constraints.append("no text or labels")
        if config.avoid_symbols:
            constraints.append("no currency symbols or specific monetary amounts")
        
        if constraints:
            prompt_parts.append(f"Important: {', '.join(constraints)}.")
        
        # Add quality guidance
        if config.quality == ImageQuality.HIGH:
            prompt_parts.append(
                "Generate with maximum detail, clarity, and visual quality."
            )
        
        return " ".join(prompt_parts)
    
    def generate_image(
        self,
        prompt: str,
        config: Optional[ImageGenerationConfig] = None,
        enhance_for_finance: bool = True,
        save_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an image using Google Gemini.
        
        Args:
            prompt: Description of the image to generate
            config: Configuration options (uses defaults if not provided)
            enhance_for_finance: Add financial application enhancements to prompt
            save_prompt: Whether to return the full prompt used
            
        Returns:
            Dictionary containing:
                - image: PIL Image object
                - format: Image format
                - prompt: Full prompt used (if save_prompt=True)
                - size: Tuple of (width, height)
                
        Raises:
            RuntimeError: If Gemini is not configured
            Exception: If generation fails
        """
        if not self._gemini_configured:
            raise RuntimeError("Gemini API not configured. Call configure_gemini() first.")
        
        config = config or ImageGenerationConfig()
        
        # Build enhanced prompt
        full_prompt = self._build_prompt(prompt, config, enhance_for_finance)
        logger.info(f"Generating image with prompt: {full_prompt[:100]}...")
        
        try:
            client = genaiClient.Client()
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=(full_prompt,),
                config=GenerateContentConfig(
                    response_modalities=[Modality.TEXT, Modality.IMAGE]
                ),
            )
            
            if not response.candidates:
                raise Exception("Gemini API did not return any candidates.")
            
            # Extract image from response
            generated_image = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_image = Image.open(BytesIO(part.inline_data.data))
                    break
            
            if not generated_image:
                raise Exception("No image found in Gemini API response.")
            
            # Resize if needed
            width, height = config.get_dimensions()
            if width and height and generated_image.size != (width, height):
                generated_image = generated_image.resize(
                    (width, height),
                    Image.Resampling.LANCZOS
                )
            
            logger.info(f"Image generated successfully: {generated_image.size}")
            
            result = {
                'image': generated_image,
                'format': config.format,
                'size': generated_image.size,
            }
            
            if save_prompt:
                result['prompt'] = full_prompt
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}", exc_info=True)
            raise
    
    def upload_image(
        self,
        image: Image.Image,
        object_key: str,
        config: Optional[ImageGenerationConfig] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload image to configured cloud storage.
        
        Args:
            image: PIL Image object to upload
            object_key: Storage path/key for the image
            config: Configuration for format and quality
            metadata: Optional metadata to attach to the object
            
        Returns:
            Public URL to the uploaded image
            
        Raises:
            RuntimeError: If storage is not configured
            ClientError: If upload fails
        """
        if not self._storage_client:
            raise RuntimeError("Storage not configured. Call configure_storage() first.")
        
        config = config or ImageGenerationConfig()
        
        # Convert image to bytes
        byte_stream = BytesIO()
        
        if config.format == "png":
            image.save(
                byte_stream,
                format='PNG',
                optimize=True,
                compress_level=config.compression_level
            )
            content_type = 'image/png'
        elif config.format == "jpeg":
            # Convert to RGB if necessary (JPEG doesn't support transparency)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            image.save(
                byte_stream,
                format='JPEG',
                quality=config.jpeg_quality,
                optimize=True
            )
            content_type = 'image/jpeg'
        elif config.format == "webp":
            image.save(
                byte_stream,
                format='WEBP',
                quality=config.jpeg_quality,
                method=6  # Best compression
            )
            content_type = 'image/webp'
        else:
            raise ValueError(f"Unsupported format: {config.format}")
        
        image_bytes = byte_stream.getvalue()
        
        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self._storage_config['bucket'],
                'Key': object_key,
                'Body': image_bytes,
                'ContentType': content_type,
            }
            
            # Add public access if configured
            if config.public_access:
                upload_params['ACL'] = 'public-read'
            
            # Add metadata if provided
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Upload to storage
            logger.info(f"Uploading image to {object_key}")
            self._storage_client.put_object(**upload_params)
            
            # Build public URL
            bucket = self._storage_config['bucket']
            region = self._storage_config['region']
            provider = self._storage_config['provider']
            
            if provider == StorageProvider.DIGITALOCEAN_SPACES:
                if config.cdn_enabled:
                    # Assume CDN endpoint follows standard pattern
                    image_url = f"https://{bucket}.{region}.cdn.digitaloceanspaces.com/{object_key}"
                else:
                    image_url = f"https://{bucket}.{region}.digitaloceanspaces.com/{object_key}"
            elif provider == StorageProvider.AWS_S3:
                if config.cdn_enabled:
                    # Would need CloudFront distribution URL
                    logger.warning("CDN URL requested but CloudFront domain not configured")
                image_url = f"https://{bucket}.s3.{region}.amazonaws.com/{object_key}"
            else:
                image_url = f"{self._storage_config['endpoint_url']}/{bucket}/{object_key}"
            
            logger.info(f"Image uploaded successfully: {image_url}")
            return image_url
            
        except ClientError as e:
            logger.error(f"Failed to upload image: {e}", exc_info=True)
            raise
    
    def generate_and_upload(
        self,
        prompt: str,
        object_key: str,
        config: Optional[ImageGenerationConfig] = None,
        enhance_for_finance: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate an image and upload it to storage in one operation.
        
        Args:
            prompt: Description of the image to generate
            object_key: Storage path/key for the image
            config: Configuration options
            enhance_for_finance: Add financial application enhancements
            metadata: Optional metadata to attach to the object
            
        Returns:
            Dictionary containing:
                - url: Public URL to the uploaded image
                - prompt: Full prompt used
                - size: Image dimensions
                - format: Image format
                
        Raises:
            RuntimeError: If Gemini or storage not configured
            Exception: If generation or upload fails
        """
        config = config or ImageGenerationConfig()
        
        # Generate image
        generation_result = self.generate_image(
            prompt=prompt,
            config=config,
            enhance_for_finance=enhance_for_finance,
            save_prompt=True
        )
        
        # Add metadata about generation
        gen_metadata = metadata or {}
        gen_metadata.update({
            'generated_by': 'gemini-2.0-flash-preview-image-generation',
            'theme': config.theme.value,
            'size': f"{generation_result['size'][0]}x{generation_result['size'][1]}",
        })
        
        # Upload image
        image_url = self.upload_image(
            image=generation_result['image'],
            object_key=object_key,
            config=config,
            metadata=gen_metadata
        )
        
        return {
            'url': image_url,
            'prompt': generation_result['prompt'],
            'size': generation_result['size'],
            'format': config.format,
        }
    
    def delete_image(self, object_key: str) -> bool:
        """
        Delete an image from storage.
        
        Args:
            object_key: Storage path/key of the image to delete
            
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
            logger.info(f"Deleted image: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete image {object_key}: {e}")
            return False


# Singleton instance getter
def get_image_generation_service() -> ImageGenerationService:
    """Get the singleton ImageGenerationService instance"""
    return ImageGenerationService()
