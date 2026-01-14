# timber/common/services/media/examples.py
"""
Practical Examples for Media Generation Service

Demonstrates common use cases for image generation in financial applications.
"""

from typing import Dict, Any
from common.services.media import (
    get_image_generation_service,
    ImageGenerationConfig,
    ImageSize,
    ImageQuality,
    ImageTheme,
    StorageProvider
)


# Example 1: Initialize Service
def initialize_service(gemini_api_key: str, storage_config: Dict[str, str]):
    """
    Initialize the image generation service.
    
    Args:
        gemini_api_key: Google Gemini API key
        storage_config: Dictionary with storage configuration
    """
    service = get_image_generation_service()
    
    # Configure Gemini
    service.configure_gemini(gemini_api_key)
    
    # Configure Storage
    service.configure_storage(
        provider=StorageProvider.DIGITALOCEAN_SPACES,
        region=storage_config['region'],
        bucket=storage_config['bucket'],
        access_key=storage_config['access_key'],
        secret_key=storage_config['secret_key']
    )
    
    return service


# Example 2: Generate Goal Image (Standard)
def generate_goal_image(goal_name: str, goal_id: int, user_id: int) -> Dict[str, Any]:
    """
    Generate a standard image for a financial goal.
    
    Args:
        goal_name: Name of the goal (e.g., "Retirement Fund")
        goal_id: Goal ID
        user_id: User ID
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    prompt = f"Visual representation of the financial goal: {goal_name}"
    object_key = f"goals/{user_id}/{goal_id}/main.png"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        metadata={
            "goal_id": str(goal_id),
            "user_id": str(user_id),
            "goal_name": goal_name,
            "type": "goal_image"
        }
    )
    
    return result


# Example 3: Generate Portfolio Snapshot (High Quality)
def generate_portfolio_snapshot(portfolio_name: str, user_id: int) -> Dict[str, Any]:
    """
    Generate high-quality image for portfolio visualization.
    
    Args:
        portfolio_name: Portfolio name
        user_id: User ID
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.WIDE_CARD,
        quality=ImageQuality.HIGH,
        theme=ImageTheme.PROFESSIONAL,
        format="png",
        compression_level=9
    )
    
    prompt = (
        f"Professional financial portfolio visualization representing {portfolio_name}. "
        "Show diversified investments, growth trends, and financial success."
    )
    
    object_key = f"portfolios/{user_id}/{portfolio_name.lower().replace(' ', '_')}.png"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config,
        metadata={
            "user_id": str(user_id),
            "portfolio_name": portfolio_name,
            "type": "portfolio_snapshot"
        }
    )
    
    return result


# Example 4: Generate Educational Content (Illustration Style)
def generate_educational_image(topic: str, concept: str) -> Dict[str, Any]:
    """
    Generate illustrated educational content.
    
    Args:
        topic: Educational topic
        concept: Specific concept to illustrate
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.STANDARD,
        quality=ImageQuality.MEDIUM,
        theme=ImageTheme.ILLUSTRATION,
        format="png"
    )
    
    prompt = (
        f"Educational illustration explaining {concept} in {topic}. "
        "Clear, simple, and engaging visual that helps understand the concept."
    )
    
    object_key = f"education/{topic.lower()}/{concept.lower().replace(' ', '_')}.png"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config,
        enhance_for_finance=True
    )
    
    return result


# Example 5: Generate Marketing Banner (High Resolution)
def generate_marketing_banner(campaign_name: str, message: str) -> Dict[str, Any]:
    """
    Generate high-resolution marketing banner.
    
    Args:
        campaign_name: Campaign name
        message: Marketing message/theme
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.BANNER,
        quality=ImageQuality.HIGH,
        theme=ImageTheme.PROFESSIONAL,
        format="jpeg",
        jpeg_quality=95
    )
    
    prompt = (
        f"Professional financial services marketing banner for {campaign_name}. "
        f"Theme: {message}. Modern, trustworthy, and inspiring."
    )
    
    object_key = f"marketing/{campaign_name.lower().replace(' ', '_')}/banner.jpg"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 6: Generate Thumbnail (Fast, Low Quality)
def generate_thumbnail(entity_type: str, entity_id: int, description: str) -> Dict[str, Any]:
    """
    Generate quick thumbnail for list views.
    
    Args:
        entity_type: Type of entity (goal, portfolio, etc.)
        entity_id: Entity ID
        description: Brief description
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.THUMBNAIL,
        quality=ImageQuality.LOW,
        theme=ImageTheme.MINIMALIST,
        format="webp",  # Smallest file size
        jpeg_quality=75
    )
    
    prompt = f"Simple icon representing: {description}"
    object_key = f"thumbnails/{entity_type}/{entity_id}.webp"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 7: Generate Abstract Data Visualization
def generate_data_visualization(metric: str, trend: str) -> Dict[str, Any]:
    """
    Generate abstract data visualization.
    
    Args:
        metric: Metric being visualized (e.g., "ROI", "Growth")
        trend: Trend description (e.g., "upward", "stable")
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.CARD,
        quality=ImageQuality.MEDIUM,
        theme=ImageTheme.INFOGRAPHIC,
        format="png"
    )
    
    prompt = (
        f"Clean infographic-style visualization showing {trend} {metric}. "
        "Abstract, data-driven, professional appearance with clear visual trend."
    )
    
    object_key = f"visualizations/{metric.lower()}/{trend}.png"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 8: Generate Custom Size Image
def generate_custom_report_header(report_type: str, dimensions: tuple) -> Dict[str, Any]:
    """
    Generate custom-sized report header.
    
    Args:
        report_type: Type of report
        dimensions: (width, height) tuple
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.CUSTOM,
        custom_width=dimensions[0],
        custom_height=dimensions[1],
        quality=ImageQuality.HIGH,
        theme=ImageTheme.PROFESSIONAL,
        format="png"
    )
    
    prompt = f"Professional header image for {report_type} financial report"
    object_key = f"reports/headers/{report_type.lower().replace(' ', '_')}.png"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 9: Generate Vintage-Style Image
def generate_vintage_concept(concept: str) -> Dict[str, Any]:
    """
    Generate vintage-style financial concept image.
    
    Args:
        concept: Financial concept to visualize
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.STANDARD,
        quality=ImageQuality.MEDIUM,
        theme=ImageTheme.VINTAGE,
        format="jpeg",
        jpeg_quality=85
    )
    
    prompt = f"Classic, timeless representation of {concept} in finance"
    object_key = f"concepts/vintage/{concept.lower().replace(' ', '_')}.jpg"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 10: Batch Generate Multiple Goal Images
def batch_generate_goal_images(goals: list) -> list:
    """
    Generate images for multiple goals efficiently.
    
    Args:
        goals: List of goal dictionaries with 'id', 'name', 'user_id'
        
    Returns:
        List of results for each goal
    """
    service = get_image_generation_service()
    results = []
    
    config = ImageGenerationConfig(
        size=ImageSize.CARD,
        quality=ImageQuality.MEDIUM,
        theme=ImageTheme.REALISTIC,
        format="png"
    )
    
    for goal in goals:
        try:
            prompt = f"Visual representation of financial goal: {goal['name']}"
            object_key = f"goals/{goal['user_id']}/{goal['id']}/main.png"
            
            result = service.generate_and_upload(
                prompt=prompt,
                object_key=object_key,
                config=config,
                metadata={
                    "goal_id": str(goal['id']),
                    "user_id": str(goal['user_id']),
                    "goal_name": goal['name']
                }
            )
            
            results.append({
                "goal_id": goal['id'],
                "success": True,
                "url": result['url']
            })
            
        except Exception as e:
            results.append({
                "goal_id": goal['id'],
                "success": False,
                "error": str(e)
            })
    
    return results


# Example 11: Generate with Custom Brand Colors
def generate_branded_image(title: str, custom_colors: list) -> Dict[str, Any]:
    """
    Generate image with specific brand colors.
    
    Args:
        title: Image title/concept
        custom_colors: List of hex color codes
        
    Returns:
        Dictionary with image URL and metadata
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.STANDARD,
        quality=ImageQuality.HIGH,
        theme=ImageTheme.PROFESSIONAL,
        brand_colors=custom_colors,
        format="png"
    )
    
    prompt = f"Professional financial image: {title}"
    object_key = f"branded/{title.lower().replace(' ', '_')}.png"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 12: Generate and Save Locally (for testing)
def generate_local_preview(description: str, output_path: str):
    """
    Generate image and save locally (for development/testing).
    
    Args:
        description: Image description
        output_path: Local path to save image
    """
    service = get_image_generation_service()
    
    config = ImageGenerationConfig(
        size=ImageSize.CARD,
        quality=ImageQuality.MEDIUM,
        theme=ImageTheme.PROFESSIONAL
    )
    
    # Generate only (don't upload)
    result = service.generate_image(
        prompt=description,
        config=config
    )
    
    # Save locally
    result['image'].save(output_path)
    print(f"Image saved to {output_path}")
    print(f"Used prompt: {result['prompt']}")


if __name__ == "__main__":
    # Example usage
    print("Media Generation Service Examples")
    print("See function docstrings for usage details")
