"""
Utilities for Telegram Bot
"""

import os
import logging
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from aiogram.types import PhotoSize, File
from aiogram import Bot
from PIL import Image
import cv2
import numpy as np

from .config import Config

logger = logging.getLogger(__name__)
config = Config()


def setup_logging():
    """Setup logging configuration"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(config.LOGS_DIR, 'bot.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def create_temp_dir():
    """Create temporary directory for files"""
    
    Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"Created temp directory: {config.TEMP_DIR}")


def create_session_id(user_id: int) -> str:
    """Create unique session ID"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_part = str(uuid.uuid4())[:8]
    
    return f"{user_id}_{timestamp}_{random_part}"


def validate_photo(photo: PhotoSize) -> bool:
    """Validate photo requirements"""
    
    try:
        # Check file size
        if photo.file_size > config.MAX_FILE_SIZE_MB * 1024 * 1024:
            logger.warning(f"Photo too large: {photo.file_size} bytes")
            return False
        
        # Check dimensions
        if photo.width < 512 or photo.height < 512:
            logger.warning(f"Photo too small: {photo.width}x{photo.height}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating photo: {e}")
        return False


async def save_photo(photo: PhotoSize, session_id: str, bot: Bot = None) -> str:
    """Save photo to temporary directory"""
    
    try:
        # Create session directory
        session_dir = Path(config.TEMP_DIR) / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Generate filename
        filename = f"photo_{photo.file_id[:10]}.jpg"
        filepath = session_dir / filename
        
        # Download photo
        if bot:
            file_info = await bot.get_file(photo.file_id)
            await bot.download_file(file_info.file_path, filepath)
        
        logger.info(f"Saved photo: {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"Error saving photo: {e}")
        raise


def analyze_photo_quality(image_path: str) -> Dict[str, Any]:
    """Analyze photo quality using OpenCV"""
    
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {"quality": "poor", "reason": "Cannot read image"}
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate blur (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate brightness
        brightness = np.mean(gray)
        
        # Face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Quality assessment
        quality = "good"
        issues = []
        
        if blur_score < 100:
            quality = "poor"
            issues.append("Image is too blurry")
        
        if brightness < 50:
            quality = "poor"
            issues.append("Image is too dark")
        elif brightness > 200:
            quality = "poor"
            issues.append("Image is too bright")
        
        if len(faces) == 0:
            quality = "poor"
            issues.append("No face detected")
        elif len(faces) > 1:
            quality = "fair"
            issues.append("Multiple faces detected")
        
        return {
            "quality": quality,
            "blur_score": blur_score,
            "brightness": brightness,
            "faces_count": len(faces),
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Error analyzing photo quality: {e}")
        return {"quality": "unknown", "reason": str(e)}


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def generate_user_hash(user_id: int) -> str:
    """Generate hash for user (for privacy)"""
    
    return hashlib.md5(str(user_id).encode()).hexdigest()[:8]


def is_session_expired(session_id: str) -> bool:
    """Check if session is expired"""
    
    try:
        # Extract timestamp from session_id
        parts = session_id.split('_')
        if len(parts) < 3:
            return True
        
        timestamp_str = parts[1]
        session_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        
        # Check if expired
        expiry_time = session_time + timedelta(minutes=config.SESSION_TIMEOUT_MINUTES)
        return datetime.now() > expiry_time
        
    except Exception as e:
        logger.error(f"Error checking session expiry: {e}")
        return True


def cleanup_old_files():
    """Clean up old temporary files"""
    
    try:
        temp_dir = Path(config.TEMP_DIR)
        if not temp_dir.exists():
            return
        
        # Delete files older than 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for file_path in temp_dir.rglob('*'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Deleted old file: {file_path}")
        
        # Delete empty directories
        for dir_path in temp_dir.iterdir():
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                logger.info(f"Deleted empty directory: {dir_path}")
                
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")


def get_photo_metadata(image_path: str) -> Dict[str, Any]:
    """Get photo metadata"""
    
    try:
        with Image.open(image_path) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "has_exif": hasattr(img, '_getexif') and img._getexif() is not None
            }
    except Exception as e:
        logger.error(f"Error getting photo metadata: {e}")
        return {}


def create_photo_preview(image_path: str, max_size: int = 256) -> str:
    """Create photo preview"""
    
    try:
        preview_path = image_path.replace('.jpg', '_preview.jpg')
        
        with Image.open(image_path) as img:
            # Calculate new size
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            # Resize and save
            preview = img.resize(new_size, Image.Resampling.LANCZOS)
            preview.save(preview_path, 'JPEG', quality=85)
        
        return preview_path
        
    except Exception as e:
        logger.error(f"Error creating photo preview: {e}")
        return image_path 