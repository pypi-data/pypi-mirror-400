# timber/common/services/media/video_examples.py
"""
Practical Examples for Video Generation Service

Demonstrates common use cases for video generation in financial applications using Veo 3.1.
"""

from typing import Dict, Any, List
from common.services.media import (
    get_video_generation_service,
    VideoGenerationConfig,
    VideoResolution,
    VideoDuration,
    VideoAspectRatio,
    VideoModel,
    VideoGenerationType,
    StorageProvider
)


# Example 1: Initialize Service
def initialize_video_service(gemini_api_key: str, storage_config: Dict[str, str]):
    """
    Initialize the video generation service.
    
    Args:
        gemini_api_key: Google Gemini API key with Veo access
        storage_config: Dictionary with storage configuration
    """
    service = get_video_generation_service()
    
    # Configure Gemini/Veo
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


# Example 2: Generate Goal Achievement Video (Standard)
def generate_goal_achievement_video(goal_name: str, goal_id: int, user_id: int) -> Dict[str, Any]:
    """
    Generate a motivational video for achieving a financial goal.
    
    Args:
        goal_name: Name of the goal (e.g., "Retirement Savings")
        goal_id: Goal ID
        user_id: User ID
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    prompt = (
        f"A cinematic sequence showing the journey toward achieving {goal_name}. "
        "Start with a person looking at their financial plans, transition to "
        "moments of discipline and smart decisions, and conclude with celebrating "
        "the achievement. Warm, inspiring, professional tone."
    )
    
    config = VideoGenerationConfig(
        duration=VideoDuration.STANDARD,  # 8 seconds
        resolution=VideoResolution.FULL_HD_1080P,
        aspect_ratio=VideoAspectRatio.LANDSCAPE,
        enable_audio=True,
        audio_description="Uplifting background music with subtle success sounds",
        cinematic_style="documentary, warm lighting, professional"
    )
    
    object_key = f"videos/goals/{user_id}/{goal_id}/achievement.mp4"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config,
        metadata={
            "goal_id": str(goal_id),
            "user_id": str(user_id),
            "goal_name": goal_name,
            "type": "goal_achievement"
        }
    )
    
    return result


# Example 3: Generate Portfolio Performance Video (High Quality)
def generate_portfolio_performance_video(
    portfolio_name: str,
    performance_metrics: Dict[str, Any],
    user_id: int
) -> Dict[str, Any]:
    """
    Generate high-quality video showcasing portfolio performance.
    
    Args:
        portfolio_name: Portfolio name
        performance_metrics: Dict with metrics (return, growth, etc.)
        user_id: User ID
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    growth = performance_metrics.get('growth_percentage', 0)
    
    config = VideoGenerationConfig(
        model=VideoModel.VEO_3_1,  # High quality model
        duration=VideoDuration.STANDARD,
        resolution=VideoResolution.FULL_HD_1080P,
        aspect_ratio=VideoAspectRatio.LANDSCAPE,
        enable_audio=True,
        audio_description="Professional business ambience with subtle growth sounds",
        cinematic_style="corporate, clean, professional, data-driven",
        camera_movements="Smooth pan across financial charts, gradual zoom on key metrics"
    )
    
    prompt = (
        f"Professional visualization of {portfolio_name} portfolio performance. "
        f"Show abstract representations of diversified investments growing by {growth}%. "
        "Display rising charts, successful trades, and positive growth trends. "
        "Modern, clean aesthetic with financial graphics. Professional and trustworthy."
    )
    
    object_key = f"videos/portfolios/{user_id}/{portfolio_name.lower().replace(' ', '_')}/performance.mp4"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config,
        metadata={
            "user_id": str(user_id),
            "portfolio_name": portfolio_name,
            "growth": str(growth),
            "type": "portfolio_performance"
        }
    )
    
    return result


# Example 4: Generate Educational Content Video
def generate_educational_video(topic: str, concept: str, duration: int = 8) -> Dict[str, Any]:
    """
    Generate educational video explaining financial concepts.
    
    Args:
        topic: Educational topic (e.g., "Investing Basics")
        concept: Specific concept to explain
        duration: Video length in seconds (4, 6, or 8)
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        duration=VideoDuration(duration),
        resolution=VideoResolution.HD_720P,
        aspect_ratio=VideoAspectRatio.LANDSCAPE,
        enable_audio=True,
        audio_description="Clear narration explaining the concept, with subtle background music",
        cinematic_style="educational, clear, engaging, animated graphics"
    )
    
    prompt = (
        f"Educational video explaining {concept} in {topic}. "
        "Use clear visual metaphors, simple animations, and engaging graphics. "
        "Show real-world applications and practical examples. "
        "Professional, trustworthy, easy to understand."
    )
    
    object_key = f"videos/education/{topic.lower()}/{concept.lower().replace(' ', '_')}.mp4"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config,
        enhance_for_finance=True
    )
    
    return result


# Example 5: Generate Marketing Video (Fast)
def generate_marketing_video(campaign_name: str, message: str) -> Dict[str, Any]:
    """
    Generate marketing video quickly for campaigns.
    
    Args:
        campaign_name: Campaign name
        message: Marketing message/theme
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        model=VideoModel.VEO_3_1_FAST,  # Faster generation
        duration=VideoDuration.SHORT,  # 4 seconds for ads
        resolution=VideoResolution.FULL_HD_1080P,
        aspect_ratio=VideoAspectRatio.LANDSCAPE,
        enable_audio=True,
        audio_description="Energetic, modern background music with call-to-action emphasis",
        cinematic_style="commercial, dynamic, eye-catching, professional"
    )
    
    prompt = (
        f"Dynamic marketing video for {campaign_name}. "
        f"Theme: {message}. "
        "Show modern financial technology, successful people, and positive outcomes. "
        "Fast-paced, engaging, trustworthy. Call-to-action feel."
    )
    
    object_key = f"videos/marketing/{campaign_name.lower().replace(' ', '_')}/ad.mp4"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 6: Generate Social Media Video (Portrait)
def generate_social_media_video(content_type: str, description: str) -> Dict[str, Any]:
    """
    Generate portrait video for social media (Instagram, TikTok, etc.).
    
    Args:
        content_type: Type of content (tip, story, etc.)
        description: Content description
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        duration=VideoDuration.MEDIUM,  # 6 seconds
        resolution=VideoResolution.HD_720P,  # Portrait doesn't support 1080p
        aspect_ratio=VideoAspectRatio.PORTRAIT,  # 9:16 for mobile
        enable_audio=True,
        audio_description="Trendy, upbeat music with engaging sounds",
        cinematic_style="social media, modern, engaging, quick cuts"
    )
    
    prompt = (
        f"Vertical video for social media about {description}. "
        "Modern, attention-grabbing, suitable for Instagram/TikTok. "
        "Fast-paced, visually interesting, mobile-optimized. "
        "Professional but approachable."
    )
    
    object_key = f"videos/social/{content_type.lower()}/{description.lower().replace(' ', '_')}.mp4"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=object_key,
        config=config
    )
    
    return result


# Example 7: Generate Video from Reference Images
def generate_video_from_references(
    prompt: str,
    reference_images: List[str],
    output_key: str
) -> Dict[str, Any]:
    """
    Generate video using reference images for character/style consistency.
    
    Args:
        prompt: Video description
        reference_images: List of 1-3 reference image URLs/paths
        output_key: Storage path for output
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        generation_type=VideoGenerationType.REFERENCE_TO_VIDEO,
        reference_images=reference_images,  # 1-3 images
        duration=VideoDuration.STANDARD,
        resolution=VideoResolution.FULL_HD_1080P,
        enable_audio=True
    )
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=output_key,
        config=config
    )
    
    return result


# Example 8: Generate Video with First and Last Frame
def generate_transition_video(
    first_frame_url: str,
    last_frame_url: str,
    transition_description: str,
    output_key: str
) -> Dict[str, Any]:
    """
    Generate video transitioning between two specific frames.
    
    Args:
        first_frame_url: URL to first frame image
        last_frame_url: URL to last frame image
        transition_description: Description of the transition
        output_key: Storage path for output
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        generation_type=VideoGenerationType.FRAME_TO_FRAME,
        first_frame=first_frame_url,
        last_frame=last_frame_url,
        duration=VideoDuration.STANDARD,
        resolution=VideoResolution.FULL_HD_1080P,
        enable_audio=True
    )
    
    prompt = f"Smooth transition: {transition_description}"
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=output_key,
        config=config
    )
    
    return result


# Example 9: Extend Existing Video
def extend_video_sequence(
    original_video_url: str,
    continuation_prompt: str,
    output_key: str
) -> Dict[str, Any]:
    """
    Extend an existing video with additional footage.
    
    Args:
        original_video_url: URL to the video to extend
        continuation_prompt: Description of how to continue
        output_key: Storage path for extended video
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    result = service.extend_video(
        video_url=original_video_url,
        prompt=continuation_prompt,
        object_key=output_key
    )
    
    return result


# Example 10: Generate Video with Specific Camera Work
def generate_cinematic_video(
    scene_description: str,
    camera_movements: str,
    output_key: str
) -> Dict[str, Any]:
    """
    Generate video with specific camera movements and cinematic style.
    
    Args:
        scene_description: Description of the scene
        camera_movements: Specific camera movements desired
        output_key: Storage path
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        duration=VideoDuration.STANDARD,
        resolution=VideoResolution.FULL_HD_1080P,
        enable_audio=True,
        audio_description="Cinematic score matching the mood",
        cinematic_style="cinematic, film-like, professional cinematography",
        camera_movements=camera_movements
    )
    
    prompt = scene_description
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=output_key,
        config=config
    )
    
    return result


# Example 11: Batch Generate Multiple Videos
def batch_generate_goal_videos(goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate videos for multiple goals efficiently.
    
    Args:
        goals: List of goal dictionaries with 'id', 'name', 'user_id'
        
    Returns:
        List of results for each goal
    """
    service = get_video_generation_service()
    results = []
    
    # Use fast model for batch operations
    config = VideoGenerationConfig(
        model=VideoModel.VEO_3_1_FAST,
        duration=VideoDuration.MEDIUM,
        resolution=VideoResolution.HD_720P,
        enable_audio=True
    )
    
    for goal in goals:
        try:
            prompt = f"Visualize achieving the financial goal: {goal['name']}"
            object_key = f"videos/goals/{goal['user_id']}/{goal['id']}/main.mp4"
            
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


# Example 12: Generate Video with Negative Prompt
def generate_controlled_video(
    prompt: str,
    avoid: str,
    output_key: str
) -> Dict[str, Any]:
    """
    Generate video while avoiding specific content.
    
    Args:
        prompt: Positive prompt describing what to generate
        avoid: Negative prompt describing what to avoid
        output_key: Storage path
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        duration=VideoDuration.STANDARD,
        resolution=VideoResolution.FULL_HD_1080P,
        negative_prompt=avoid
    )
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=output_key,
        config=config
    )
    
    return result


# Example 13: Generate Reproducible Video (with Seed)
def generate_reproducible_video(
    prompt: str,
    seed: int,
    output_key: str
) -> Dict[str, Any]:
    """
    Generate video with a specific seed for reproducibility.
    
    Args:
        prompt: Video description
        seed: Random seed (for consistent results)
        output_key: Storage path
        
    Returns:
        Dictionary with video URL and metadata
    """
    service = get_video_generation_service()
    
    config = VideoGenerationConfig(
        duration=VideoDuration.STANDARD,
        resolution=VideoResolution.FULL_HD_1080P,
        seed=seed  # Same seed = similar output
    )
    
    result = service.generate_and_upload(
        prompt=prompt,
        object_key=output_key,
        config=config
    )
    
    return result


if __name__ == "__main__":
    # Example usage
    print("Video Generation Service Examples")
    print("See function docstrings for usage details")
    print("\nNote: Requires Gemini API key with Veo 3.1 access")
