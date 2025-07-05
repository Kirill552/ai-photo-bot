"""
Image processing tasks for Yandex Message Queue
"""

import os
import logging
from typing import Dict, Any, List
import httpx
import asyncio

from .image_generator import ImageGenerator
from .storage import YandexObjectStorage
from .prompts import PromptGenerator
from .utils import create_image_album, optimize_image
from .config import settings
from .notifications import TelegramNotifier

logger = logging.getLogger(__name__)


def process_image_generation_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process image generation task from YC Message Queue"""
    
    logger.info(f"🎨 Starting image generation task: {task_data}")
    
    try:
        # Extract data
        user_id = task_data['user_id']
        session_id = task_data['session_id']
        brief = task_data['brief']
        photos = task_data['photos']
        
        # Initialize components
        image_generator = ImageGenerator('flux')
        prompt_generator = PromptGenerator()
        
        # Generate prompts based on brief
        prompts = prompt_generator.generate_prompts(brief)
        logger.info(f"📝 Generated {len(prompts)} prompts for user {user_id}")
        
        # Generate images
        generated_images = []
        for i, prompt in enumerate(prompts):
            try:
                # Choose generator based on brief
                generator = brief.get('generator', 'flux')
                
                if generator == 'flux':
                    image_urls = image_generator.generate_with_flux(
                        prompt=prompt,
                        reference_images=photos,
                        lora_type=brief.get('lora_type', 'realism')
                    )
                else:
                    image_urls = image_generator.generate_with_gpt(
                        prompt=prompt,
                        reference_images=photos
                    )
                
                generated_images.extend(image_urls)
                
                logger.info(f"✨ Generated {len(image_urls)} images for prompt {i+1}")
                
            except Exception as e:
                logger.error(f"❌ Error generating image {i}: {e}")
                continue
        
        logger.info(f"🎉 Generated {len(generated_images)} total images for user {user_id}")
        
        # Upload to storage
        upload_result = upload_to_storage(
            user_id=user_id,
            session_id=session_id,
            image_urls=generated_images,
            brief=brief
        )
        
        # Check if video generation is needed
        if brief.get('package_type') in ['standard', 'premium'] and brief.get('enable_video', False):
            # Generate video from best image
            if upload_result.get('uploaded_urls'):
                video_result = generate_video(
                    user_id=user_id,
                    session_id=session_id,
                    best_image_url=upload_result['uploaded_urls'][0],
                    brief=brief
                )
                upload_result['video_url'] = video_result.get('video_url')
        
        # Post-process for premium package
        if brief.get('package_type') == 'premium' and brief.get('enable_post_process', False):
            if upload_result.get('uploaded_urls'):
                post_process_result = post_process_images(
                    user_id=user_id,
                    session_id=session_id,
                    image_paths=upload_result['uploaded_urls'],
                    brief=brief
                )
                upload_result['post_processed_urls'] = post_process_result.get('processed_urls')
        
        # Notify user about success
        notify_user_success(user_id, upload_result)
        
        return {
            'success': True,
            'images_generated': len(generated_images),
            'result': upload_result
        }
        
    except Exception as e:
        logger.error(f"❌ Error in process_image_generation_task: {e}")
        notify_user_error(user_id, str(e))
        return {
            'success': False,
            'error': str(e)
        }


def upload_to_storage(user_id: int, session_id: str, image_urls: List[str], brief: Dict[str, Any]) -> Dict[str, Any]:
    """Upload images to Yandex Cloud Storage"""
    
    logger.info(f"☁️ Starting storage upload for user {user_id}")
    
    try:
        # Initialize storage
        storage = YandexObjectStorage()
        
        # Download and optimize images
        local_images = []
        for i, url in enumerate(image_urls):
            try:
                # Download image
                local_path = f"/tmp/worker/{session_id}/image_{i}.jpg"
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # Download from URL
                with httpx.stream('GET', url) as response:
                    response.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                
                # Optimize image
                optimized_path = optimize_image(local_path)
                local_images.append(optimized_path)
                
                logger.info(f"⬇️ Downloaded image {i + 1}/{len(image_urls)}")
                
            except Exception as e:
                logger.error(f"❌ Error downloading image {i}: {e}")
                continue
        
        # Upload to storage
        uploaded_urls = []
        for i, local_path in enumerate(local_images):
            try:
                # Upload to storage
                key = f"sessions/{session_id}/images/image_{i}.jpg"
                url = storage.upload_file(local_path, key)
                uploaded_urls.append(url)
                
                logger.info(f"⬆️ Uploaded image {i + 1}/{len(local_images)}")
                
            except Exception as e:
                logger.error(f"❌ Error uploading image {i}: {e}")
                continue
        
        # Create album/zip if needed
        album_url = None
        if len(uploaded_urls) > 50:
            # Create zip archive for large collections
            zip_path = create_image_album(local_images, session_id)
            if zip_path:
                album_key = f"sessions/{session_id}/album.zip"
                album_url = storage.upload_file(zip_path, album_key)
        
        logger.info(f"✅ Upload complete: {len(uploaded_urls)} images uploaded")
        
        return {
            'success': True,
            'uploaded_urls': uploaded_urls,
            'album_url': album_url,
            'total_images': len(uploaded_urls)
        }
        
    except Exception as e:
        logger.error(f"❌ Error in upload_to_storage: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def notify_user_success(user_id: int, result: Dict[str, Any]) -> bool:
    """Notify user about successful generation"""
    
    try:
        notifier = TelegramNotifier(settings.BOT_TOKEN)
        
        total_images = result.get('total_images', 0)
        album_url = result.get('album_url')
        video_url = result.get('video_url')
        post_processed_urls = result.get('post_processed_urls', [])
        
        message = f"🎉 Ваша фотосессия готова!\n\n"
        message += f"📸 Создано изображений: {total_images}\n"
        
        if video_url:
            message += f"🎬 Видео создано\n"
            
        if post_processed_urls:
            message += f"✨ Применена премиум обработка\n"
            
        if album_url:
            message += f"\n📁 Скачать архив: {album_url}"
        
        return notifier.send_message(user_id, message)
        
    except Exception as e:
        logger.error(f"❌ Error notifying user {user_id}: {e}")
        return False


def notify_user_error(user_id: int, error_message: str) -> bool:
    """Notify user about error"""
    
    try:
        notifier = TelegramNotifier(settings.BOT_TOKEN)
        
        message = f"❌ Произошла ошибка при создании фотосессии:\n\n{error_message}\n\n"
        message += "Попробуйте еще раз или обратитесь в поддержку."
        
        return notifier.send_message(user_id, message)
        
    except Exception as e:
        logger.error(f"❌ Error notifying user {user_id} about error: {e}")
        return False


def generate_video(user_id: int, session_id: str, best_image_url: str, brief: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video from best image"""
    
    logger.info(f"🎬 Starting video generation for user {user_id}")
    
    try:
        # Initialize video generator
        from .video_generator import VideoGenerator
        video_generator = VideoGenerator()
        
        # Generate video
        video_url = video_generator.generate_video(
            image_url=best_image_url,
            prompt=brief.get('video_prompt', ''),
            duration=brief.get('video_duration', 6),
            style=brief.get('style_code', 'RL-01')
        )
        
        if video_url:
            logger.info(f"✅ Video generated successfully for user {user_id}")
            return {
                'success': True,
                'video_url': video_url
            }
        else:
            logger.error(f"❌ Video generation failed for user {user_id}")
            return {
                'success': False,
                'error': 'Video generation failed'
            }
            
    except Exception as e:
        logger.error(f"❌ Error in generate_video: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def post_process_images(user_id: int, session_id: str, image_paths: List[str], brief: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process images for premium package"""
    
    logger.info(f"✨ Starting post-processing for user {user_id}")
    
    try:
        # Initialize post-processor
        from .post_processor import PostProcessor
        post_processor = PostProcessor()
        
        processed_urls = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Process image
                processed_url = post_processor.process_image(
                    image_url=image_path,
                    session_id=session_id,
                    settings={
                        'nsfw_filter': True,
                        'face_restoration': True,
                        'upscale_4k': True,
                        'color_enhancement': True
                    }
                )
                
                if processed_url:
                    processed_urls.append(processed_url)
                    logger.info(f"✅ Processed image {i + 1}/{len(image_paths)}")
                
            except Exception as e:
                logger.error(f"❌ Error processing image {i}: {e}")
                continue
        
        logger.info(f"✅ Post-processing complete: {len(processed_urls)} images processed")
        
        return {
            'success': True,
            'processed_urls': processed_urls,
            'total_processed': len(processed_urls)
        }
        
    except Exception as e:
        logger.error(f"❌ Error in post_process_images: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def cleanup_old_files():
    """Clean up old temporary files"""
    
    logger.info("🧹 Starting cleanup of old files")
    
    try:
        temp_dir = "/tmp/worker"
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            logger.info("✅ Cleanup completed")
        
    except Exception as e:
        logger.error(f"❌ Error in cleanup: {e}") 