"""
Utilities for Worker
"""

import os
import logging
import zipfile
from typing import List, Optional
from PIL import Image, ImageOps
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def optimize_image(image_path: str, max_size: tuple = (2048, 2048), quality: int = 85) -> str:
    """Optimize image for web delivery"""
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Auto-orient based on EXIF
            img = ImageOps.exif_transpose(img)
            
            # Save optimized version
            optimized_path = image_path.replace('.jpg', '_optimized.jpg')
            img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
            
            logger.info(f"Optimized image: {image_path} -> {optimized_path}")
            return optimized_path
            
    except Exception as e:
        logger.error(f"Error optimizing image {image_path}: {e}")
        return image_path


def create_image_album(image_paths: List[str], session_id: str) -> str:
    """Create zip archive from images"""
    
    try:
        # Create temp file for zip
        temp_dir = f"/tmp/worker/{session_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        zip_path = os.path.join(temp_dir, f"album_{session_id}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, image_path in enumerate(image_paths):
                if os.path.exists(image_path):
                    # Add image to zip with sequential name
                    arcname = f"photo_{i+1:03d}.jpg"
                    zipf.write(image_path, arcname)
        
        logger.info(f"Created album with {len(image_paths)} images: {zip_path}")
        return zip_path
        
    except Exception as e:
        logger.error(f"Error creating album: {e}")
        raise


def create_preview(image_path: str, size: tuple = (512, 512)) -> str:
    """Create preview of image"""
    
    try:
        with Image.open(image_path) as img:
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save preview
            preview_path = image_path.replace('.jpg', '_preview.jpg')
            img.save(preview_path, 'JPEG', quality=85)
            
            return preview_path
            
    except Exception as e:
        logger.error(f"Error creating preview: {e}")
        return image_path


def validate_image(image_path: str) -> bool:
    """Validate image file"""
    
    try:
        with Image.open(image_path) as img:
            # Check if image can be opened
            img.verify()
            
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning(f"Image too large: {file_size} bytes")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Invalid image {image_path}: {e}")
        return False


def cleanup_temp_files(session_id: str):
    """Clean up temporary files for session"""
    
    try:
        temp_dir = f"/tmp/worker/{session_id}"
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temp files for session: {session_id}")
            
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")


def get_image_info(image_path: str) -> dict:
    """Get image information"""
    
    try:
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size': os.path.getsize(image_path)
            }
            
    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        return {} 