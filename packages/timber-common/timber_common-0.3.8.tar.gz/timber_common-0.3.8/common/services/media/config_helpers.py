# timber/common/services/media/config_helpers.py
"""
Configuration Helper Methods for Media Services

Provides convenience methods to integrate media service configuration
with the main Config class.
"""

from typing import Dict, Any, Optional


def get_media_config_methods():
    """
    Returns dictionary of methods to add to Config class for media services.
    
    Usage:
        # In your application initialization:
        from common.utils.config import config
        
        # Get Gemini configuration
        gemini_config = config.get_gemini_config()
        
        # Get storage configuration
        storage_config = config.get_media_storage_config()
        
        # Get brand configuration
        brand_config = config.get_brand_config()
    """
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """
        Returns Google Gemini API configuration for image generation.
        
        Returns:
            Dictionary with:
                - api_key: Gemini API key
                - model: Model identifier
                - configured: Whether API key is available
        """
        return {
            "api_key": self.GEMINI_API_KEY,
            "model": "gemini-2.0-flash-preview-image-generation",
            "configured": bool(self.GEMINI_API_KEY),
        }
    
    def get_media_storage_config(self, provider: str = "digitalocean") -> Dict[str, Any]:
        """
        Returns cloud storage configuration for media files.
        
        Args:
            provider: Storage provider ('digitalocean' or 'aws')
            
        Returns:
            Dictionary with storage configuration
        """
        if provider.lower() in ("digitalocean", "digitalocean_spaces"):
            return {
                "provider": "digitalocean_spaces",
                "access_key": self.DIGITALOCEAN_SPACES_KEY,
                "secret_key": self.DIGITALOCEAN_SPACES_SECRET,
                "region": self.DIGITALOCEAN_SPACES_REGION,
                "bucket": self.DIGITALOCEAN_SPACES_BUCKET,
                "endpoint_url": f"https://{self.DIGITALOCEAN_SPACES_REGION}.digitaloceanspaces.com",
                "cdn_url": self.DIGITALOCEAN_SPACES_CDN,
                "configured": all([
                    self.DIGITALOCEAN_SPACES_KEY,
                    self.DIGITALOCEAN_SPACES_SECRET,
                    self.DIGITALOCEAN_SPACES_BUCKET
                ]),
            }
        elif provider.lower() in ("aws", "aws_s3", "s3"):
            # AWS S3 configuration (add these to your .env if using AWS)
            return {
                "provider": "aws_s3",
                "access_key": self.AWS_ACCESS_KEY_ID if hasattr(self, 'AWS_ACCESS_KEY_ID') else None,
                "secret_key": self.AWS_SECRET_ACCESS_KEY if hasattr(self, 'AWS_SECRET_ACCESS_KEY') else None,
                "region": self.AWS_REGION if hasattr(self, 'AWS_REGION') else "us-east-1",
                "bucket": self.AWS_S3_BUCKET if hasattr(self, 'AWS_S3_BUCKET') else None,
                "endpoint_url": None,  # AWS S3 uses standard endpoints
                "cdn_url": self.AWS_CLOUDFRONT_URL if hasattr(self, 'AWS_CLOUDFRONT_URL') else None,
                "configured": False,  # Set based on AWS credentials
            }
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")
    
    def get_brand_config(self) -> Dict[str, Any]:
        """
        Returns brand configuration for media generation.
        
        Returns:
            Dictionary with:
                - primary_color: Primary brand color
                - secondary_color: Secondary brand color
                - colors_hex: List of hex color codes
                - style: Brand style preference
        """
        # Convert color names to hex codes (you can expand this mapping)
        color_map = {
            "blue": "#0066CC",
            "green": "#00AA66",
            "red": "#CC0000",
            "purple": "#6600CC",
            "orange": "#FF6600",
            "teal": "#00B8A9",
            "navy": "#003366",
            "gold": "#FFD700",
        }
        
        primary_hex = color_map.get(self.BRAND_PRIMARY_COLOR.lower(), self.BRAND_PRIMARY_COLOR)
        secondary_hex = color_map.get(self.BRAND_SECONDARY_COLOR.lower(), self.BRAND_SECONDARY_COLOR)
        
        return {
            "primary_color": self.BRAND_PRIMARY_COLOR,
            "secondary_color": self.BRAND_SECONDARY_COLOR,
            "colors_hex": [primary_hex, secondary_hex],
            "style": self.BRAND_STYLE,
        }
    
    def validate_media_config(self) -> Dict[str, bool]:
        """
        Validate media service configuration.
        
        Returns:
            Dictionary with validation status for each service
        """
        return {
            "gemini_configured": bool(self.GEMINI_API_KEY),
            "storage_configured": all([
                self.DIGITALOCEAN_SPACES_KEY,
                self.DIGITALOCEAN_SPACES_SECRET,
                self.DIGITALOCEAN_SPACES_BUCKET
            ]),
            "brand_configured": all([
                self.BRAND_PRIMARY_COLOR,
                self.BRAND_SECONDARY_COLOR
            ]),
        }
    
    def get_full_media_config(self) -> Dict[str, Any]:
        """
        Get complete media service configuration.
        
        Returns:
            Dictionary with all media-related configuration
        """
        return {
            "gemini": self.get_gemini_config(),
            "storage": self.get_media_storage_config(),
            "brand": self.get_brand_config(),
            "validation": self.validate_media_config(),
        }
    
    return {
        'get_gemini_config': get_gemini_config,
        'get_media_storage_config': get_media_storage_config,
        'get_brand_config': get_brand_config,
        'validate_media_config': validate_media_config,
        'get_full_media_config': get_full_media_config,
    }


def extend_config_class(config_class):
    """
    Extend Config class with media service methods.
    
    Args:
        config_class: The Config class to extend
        
    Usage:
        from common.utils.config import Config
        from common.services.media.config_helpers import extend_config_class
        
        extend_config_class(Config)
    """
    methods = get_media_config_methods()
    for name, method in methods.items():
        setattr(config_class, name, method)
