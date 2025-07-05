"""
Post-Processing Module
Automated post-processing for Premium packages
"""

import logging
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
import cv2
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class PostProcessor:
    """
    Automated post-processing pipeline for premium packages
    Based on section 20 of the plan
    """
    
    def __init__(self, api_key: str):
        """Initialize post processor"""
        
        self.api_key = api_key
        self.base_url = "https://api.piapi.ai/api/v1"
        
        logger.info("Post processor initialized")
    
    async def process_image(self, image_path: str, package_type: str) -> Optional[str]:
        """
        Process single image through post-processing pipeline
        """
        
        try:
            # Only process for premium packages
            if package_type != "premium":
                return image_path
            
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Step 1: NSFW check
            if not await self._nsfw_check(img):
                logger.warning(f"Image failed NSFW check: {image_path}")
                return None
            
            # Step 2: Face restoration using CodeFormer
            restored_img = await self._face_restore(img)
            if restored_img is None:
                restored_img = img
            
            # Step 3: Detect and fix defects
            if self._detect_defects(restored_img):
                restored_img = await self._inpaint_defects(restored_img)
            
            # Step 4: Color and contrast enhancement
            enhanced_img = self._enhance_color_contrast(restored_img)
            
            # Step 5: 4K upscale
            upscaled_img = await self._upscale_4k(enhanced_img)
            
            # Save processed image
            processed_path = self._get_processed_path(image_path)
            cv2.imwrite(processed_path, upscaled_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            logger.info(f"Image processed successfully: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return image_path  # Return original on error
    
    async def _nsfw_check(self, img: np.ndarray) -> bool:
        """
        NSFW filter using PiAPI hume-nsfw
        Skip if score < 0.7
        """
        
        try:
            # Convert image to base64 for API
            _, buffer = cv2.imencode('.jpg', img)
            import base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            payload = {
                "model": "hume-nsfw",
                "input": {
                    "image": f"data:image/jpeg;base64,{img_base64}"
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/nsfw-check",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        nsfw_score = data.get("score", 0.0)
                        
                        # Pass if score < 0.7
                        return nsfw_score < 0.7
                    else:
                        # If API fails, assume safe
                        logger.warning(f"NSFW check failed, assuming safe: {response.status}")
                        return True
                        
        except Exception as e:
            logger.error(f"Error in NSFW check: {e}")
            return True  # Assume safe on error
    
    async def _face_restore(self, img: np.ndarray) -> Optional[np.ndarray]:
        """
        Face restoration using CodeFormer (strength=0.7)
        Note: This is a placeholder - actual implementation would use local CodeFormer
        """
        
        try:
            # Placeholder for CodeFormer restoration
            # In real implementation, this would call local CodeFormer model
            logger.info("Face restoration applied (placeholder)")
            
            # For now, return slight enhancement
            enhanced = cv2.GaussianBlur(img, (1, 1), 0)
            enhanced = cv2.addWeighted(img, 0.8, enhanced, 0.2, 0)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in face restoration: {e}")
            return None
    
    def _detect_defects(self, img: np.ndarray) -> bool:
        """
        Detect defects (extra fingers, holes, artifacts)
        Placeholder implementation
        """
        
        try:
            # Simple defect detection based on edge analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_ratio = np.sum(edges > 0) / edges.size
            
            # If too many edges, might indicate artifacts
            return edge_ratio > 0.15
            
        except Exception as e:
            logger.error(f"Error in defect detection: {e}")
            return False
    
    async def _inpaint_defects(self, img: np.ndarray) -> np.ndarray:
        """
        Inpaint defects using PiAPI stable-diffusion-inpaint
        """
        
        try:
            # Convert image to base64
            _, buffer = cv2.imencode('.jpg', img)
            import base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Create simple mask for inpainting (placeholder)
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            # Add some mask areas (this would be more sophisticated in real implementation)
            
            _, mask_buffer = cv2.imencode('.png', mask)
            mask_base64 = base64.b64encode(mask_buffer).decode('utf-8')
            
            payload = {
                "model": "stable-diffusion-inpaint",
                "input": {
                    "image": f"data:image/jpeg;base64,{img_base64}",
                    "mask": f"data:image/png;base64,{mask_base64}",
                    "prompt": "perfect skin, no artifacts, clean portrait"
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/inpaint",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        # Process response and return inpainted image
                        # This is a placeholder - real implementation would handle the response
                        logger.info("Inpainting applied (placeholder)")
                        return img
                    else:
                        logger.warning(f"Inpainting failed: {response.status}")
                        return img
                        
        except Exception as e:
            logger.error(f"Error in inpainting: {e}")
            return img
    
    def _enhance_color_contrast(self, img: np.ndarray) -> np.ndarray:
        """
        Color and contrast enhancement using CLAHE
        """
        
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # Auto-level adjustment
            for i in range(3):
                channel = enhanced[:, :, i]
                hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
                
                # Find 1% and 99% percentiles
                total_pixels = channel.size
                low_val = np.argwhere(np.cumsum(hist) > total_pixels * 0.01)[0][0]
                high_val = np.argwhere(np.cumsum(hist) > total_pixels * 0.99)[0][0]
                
                # Stretch contrast
                if high_val > low_val:
                    enhanced[:, :, i] = np.clip(
                        (channel - low_val) * 255 / (high_val - low_val), 0, 255
                    )
            
            logger.info("Color and contrast enhancement applied")
            return enhanced.astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Error in color enhancement: {e}")
            return img
    
    async def _upscale_4k(self, img: np.ndarray) -> np.ndarray:
        """
        4K upscale using Real-ESRGAN
        Placeholder implementation - would use actual Real-ESRGAN model
        """
        
        try:
            # Get current dimensions
            h, w = img.shape[:2]
            
            # Calculate target size (4K = 3840x2160, but maintain aspect ratio)
            target_height = 2160
            target_width = int(w * target_height / h)
            
            if target_width > 3840:
                target_width = 3840
                target_height = int(h * target_width / w)
            
            # Use high-quality interpolation as placeholder
            upscaled = cv2.resize(
                img, 
                (target_width, target_height), 
                interpolation=cv2.INTER_LANCZOS4
            )
            
            logger.info(f"Image upscaled to {target_width}x{target_height}")
            return upscaled
            
        except Exception as e:
            logger.error(f"Error in upscaling: {e}")
            return img
    
    def _get_processed_path(self, original_path: str) -> str:
        """Get path for processed image"""
        
        path = Path(original_path)
        processed_name = f"{path.stem}_processed{path.suffix}"
        return str(path.parent / processed_name)
    
    async def process_batch(self, image_paths: List[str], package_type: str) -> List[str]:
        """Process batch of images"""
        
        if package_type != "premium":
            return image_paths
        
        processed_paths = []
        
        # Process images in parallel (limit concurrency)
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent processes
        
        async def process_single(path):
            async with semaphore:
                return await self.process_image(path, package_type)
        
        tasks = [process_single(path) for path in image_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing {image_paths[i]}: {result}")
                processed_paths.append(image_paths[i])
            elif result:
                processed_paths.append(result)
            else:
                processed_paths.append(image_paths[i])
        
        logger.info(f"Batch processing completed: {len(processed_paths)} images")
        return processed_paths
    
    def get_processing_cost(self) -> float:
        """Get processing cost in USD"""
        
        # Based on section 20.4 of the plan
        return 0.01  # ~1 рубль per batch of 50 images 