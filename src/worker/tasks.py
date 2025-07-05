"""
Celery tasks for image processing
"""

import os
import logging
from typing import Dict, Any, List
from celery import Task
from celery.exceptions import Retry

from .celery_app import app
from .image_generator import ImageGenerator
from .storage import YandexCloudStorage
from .prompts import PromptGenerator
from .utils import create_image_album, optimize_image
from .config import WorkerConfig

logger = logging.getLogger(__name__)
config = WorkerConfig()


class BaseTask(Task):
    """Base task with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Task {task_id} failed: {exc}")
        
        # Notify user about failure
        try:
            user_id = kwargs.get('user_id') or args[0].get('user_id')
            if user_id:
                notify_user_error.delay(user_id, str(exc))
        except Exception as e:
            logger.error(f"Failed to notify user about error: {e}")


@app.task(bind=True, base=BaseTask, name='worker.tasks.generate_images')
def generate_images(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate images based on brief"""
    
    logger.info(f"Starting image generation task: {task_data}")
    
    try:
        # Extract data
        user_id = task_data['user_id']
        session_id = task_data['session_id']
        brief = task_data['brief']
        photos = task_data['photos']
        
        # Initialize components
        image_generator = ImageGenerator(
            piapi_key=config.PIAPI_KEY,
            openai_key=config.OPENAI_KEY
        )
        
        prompt_generator = PromptGenerator()
        
        # Generate prompts based on brief
        prompts = prompt_generator.generate_prompts(brief)
        logger.info(f"Generated {len(prompts)} prompts for user {user_id}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(prompts), 'status': 'Generating images...'}
        )
        
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
                
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(prompts),
                        'status': f'Generated {len(generated_images)} images...'
                    }
                )
                
            except Exception as e:
                logger.error(f"Error generating image {i}: {e}")
                continue
        
        logger.info(f"Generated {len(generated_images)} images for user {user_id}")
        
        # Start upload to storage
        upload_task = upload_to_storage.delay(
            user_id=user_id,
            session_id=session_id,
            image_urls=generated_images,
            brief=brief
        )
        
        return {
            'status': 'success',
            'images_generated': len(generated_images),
            'upload_task_id': upload_task.id
        }
        
    except Exception as e:
        logger.error(f"Error in generate_images task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@app.task(bind=True, base=BaseTask, name='worker.tasks.upload_to_storage')
def upload_to_storage(self, user_id: int, session_id: str, image_urls: List[str], brief: Dict[str, Any]) -> Dict[str, Any]:
    """Upload images to Yandex Cloud Storage"""
    
    logger.info(f"Starting storage upload for user {user_id}")
    
    try:
        # Initialize storage
        storage = YandexCloudStorage(
            access_key=config.YC_ACCESS_KEY,
            secret_key=config.YC_SECRET_KEY,
            bucket_name=config.YC_BUCKET_NAME,
            endpoint_url=config.YC_ENDPOINT
        )
        
        # Download and optimize images
        local_images = []
        for i, url in enumerate(image_urls):
            try:
                # Download image
                local_path = f"/tmp/worker/{session_id}/image_{i}.jpg"
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # Download from URL
                import httpx
                with httpx.stream('GET', url) as response:
                    response.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                
                # Optimize image
                optimized_path = optimize_image(local_path)
                local_images.append(optimized_path)
                
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(image_urls),
                        'status': f'Downloaded {i + 1} images...'
                    }
                )
                
            except Exception as e:
                logger.error(f"Error downloading image {i}: {e}")
                continue
        
        # Upload to storage
        uploaded_urls = []
        for i, local_path in enumerate(local_images):
            try:
                # Upload to storage
                key = f"sessions/{session_id}/images/image_{i}.jpg"
                url = storage.upload_file(local_path, key)
                uploaded_urls.append(url)
                
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(local_images),
                        'status': f'Uploaded {i + 1} images...'
                    }
                )
                
            except Exception as e:
                logger.error(f"Error uploading image {i}: {e}")
                continue
        
        # Create album/zip if needed
        if len(uploaded_urls) > 50:
            # Create zip archive for large collections
            zip_path = create_image_album(local_images, session_id)
            zip_key = f"sessions/{session_id}/album.zip"
            zip_url = storage.upload_file(zip_path, zip_key)
            
            result = {
                'status': 'success',
                'delivery_type': 'zip',
                'zip_url': zip_url,
                'images_count': len(uploaded_urls)
            }
        else:
            # Send as media group
            result = {
                'status': 'success',
                'delivery_type': 'media_group',
                'image_urls': uploaded_urls[:50],  # Telegram limit
                'images_count': len(uploaded_urls)
            }
        
        # Cleanup local files
        for path in local_images:
            try:
                os.remove(path)
            except Exception as e:
                logger.warning(f"Failed to cleanup file {path}: {e}")
        
        # Notify user
        notify_user_success.delay(user_id, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in upload_to_storage task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@app.task(bind=True, base=BaseTask, name='worker.tasks.notify_user')
def notify_user_success(self, user_id: int, result: Dict[str, Any]) -> bool:
    """Notify user about successful completion"""
    
    try:
        # Import here to avoid circular imports
        from .notifications import TelegramNotifier
        
        notifier = TelegramNotifier(config.BOT_TOKEN)
        
        if result['delivery_type'] == 'zip':
            message = f"🎉 Твоя фотосессия готова!\n\n" \
                     f"📸 Сгенерировано: {result['images_count']} фотографий\n" \
                     f"📁 Скачать альбом: {result['zip_url']}"
        else:
            message = f"🎉 Твоя фотосессия готова!\n\n" \
                     f"📸 Сгенерировано: {result['images_count']} фотографий\n" \
                     f"Отправляю фото..."
        
        # Send notification
        notifier.send_message(user_id, message)
        
        # Send media group if needed
        if result['delivery_type'] == 'media_group':
            notifier.send_media_group(user_id, result['image_urls'])
        
        return True
        
    except Exception as e:
        logger.error(f"Error notifying user {user_id}: {e}")
        return False


@app.task(bind=True, base=BaseTask, name='worker.tasks.notify_user_error')
def notify_user_error(self, user_id: int, error_message: str) -> bool:
    """Notify user about error"""
    
    try:
        from .notifications import TelegramNotifier
        
        notifier = TelegramNotifier(config.BOT_TOKEN)
        
        message = f"❌ Произошла ошибка при генерации фотографий.\n\n" \
                 f"Попробуй еще раз или обратись в поддержку.\n\n" \
                 f"Код ошибки: {error_message[:100]}"
        
        notifier.send_message(user_id, message)
        
        return True
        
    except Exception as e:
        logger.error(f"Error notifying user about error: {e}")
        return False


@app.task(bind=True, base=BaseTask, name='worker.tasks.generate_video')
def generate_video(self, user_id: int, session_id: str, best_image_url: str, brief: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video for Standard/Premium packages"""
    
    logger.info(f"Starting video generation for user {user_id}")
    
    try:
        # Import video generator
        from .video_generator import VideoGenerator
        video_gen = VideoGenerator(config.PIAPI_KEY)
        
        # Check if video generation is needed
        package_type = brief.get('package_type', 'basic')
        if not video_gen.should_generate_video(package_type):
            logger.info(f"Package {package_type} does not include video")
            return {'status': 'skipped', 'reason': 'package_does_not_include_video'}
        
        # Generate videos based on package
        video_count = video_gen.get_video_count(package_type)
        style = brief.get('style', 'RL-01')
        
        generated_videos = []
        
        for i in range(video_count):
            try:
                if i == 0 or package_type == "standard":
                    # Generate short video
                    import asyncio
                    video_url = asyncio.run(video_gen.make_short_video(best_image_url, style, brief))
                else:
                    # Generate long video for premium
                    import asyncio
                    video_url = asyncio.run(video_gen.make_long_video(best_image_url, style, brief))
                
                if video_url:
                    generated_videos.append(video_url)
                    
                    # Update progress
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': video_count,
                            'status': f'Generated {i + 1} videos...'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error generating video {i}: {e}")
                continue
        
        logger.info(f"Generated {len(generated_videos)} videos for user {user_id}")
        
        return {
            'status': 'success',
            'videos_generated': len(generated_videos),
            'video_urls': generated_videos
        }
        
    except Exception as e:
        logger.error(f"Error in generate_video task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=2)


@app.task(bind=True, base=BaseTask, name='worker.tasks.post_process_images')
def post_process_images(self, user_id: int, session_id: str, image_paths: List[str], brief: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process images for Premium packages"""
    
    logger.info(f"Starting post-processing for user {user_id}")
    
    try:
        # Import post processor
        from .post_processor import PostProcessor
        post_proc = PostProcessor(config.PIAPI_KEY)
        
        # Check if post-processing is needed
        package_type = brief.get('package_type', 'basic')
        if package_type != 'premium':
            logger.info(f"Package {package_type} does not include post-processing")
            return {'status': 'skipped', 'reason': 'package_does_not_include_post_processing'}
        
        # Process images in batch
        import asyncio
        processed_paths = asyncio.run(post_proc.process_batch(image_paths, package_type))
        
        logger.info(f"Post-processed {len(processed_paths)} images for user {user_id}")
        
        return {
            'status': 'success',
            'images_processed': len(processed_paths),
            'processed_paths': processed_paths
        }
        
    except Exception as e:
        logger.error(f"Error in post_process_images task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=2)


@app.task(name='worker.tasks.cleanup_old_files')
def cleanup_old_files():
    """Cleanup old temporary files"""
    
    try:
        import shutil
        from datetime import datetime, timedelta
        
        temp_dir = "/tmp/worker"
        if not os.path.exists(temp_dir):
            return
        
        # Delete directories older than 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                # Check modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                if mod_time < cutoff_time:
                    shutil.rmtree(item_path)
                    logger.info(f"Deleted old directory: {item_path}")
        
        return {"status": "success", "cleaned_up": True}
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_files: {e}")
        return {"status": "error", "message": str(e)} 