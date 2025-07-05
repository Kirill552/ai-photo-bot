"""
Video Generation Module
Generates short videos for Standard and Premium packages using WanX API
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import aiohttp
import os
from .config import Config

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Video generation using WanX img2video-14b-lora"""
    
    def __init__(self, api_key: str):
        """Initialize video generator"""
        
        self.api_key = api_key
        self.base_url = "https://api.piapi.ai/api/v1"
        self.config = Config()
        
        logger.info("Video generator initialized")
    
    async def make_short_video(self, img_url: str, style: str, brief: Dict[str, Any]) -> Optional[str]:
        """
        Generate short video using WanX img2video-14b-lora
        Based on section 21.1 of the plan
        """
        
        try:
            # Get style code for LoRA
            from .prompts import PromptGenerator
            prompt_gen = PromptGenerator()
            lora_type = prompt_gen.get_style_code(style)
            
            # Build prompt
            style_name = prompt_gen.style_templates.get(style, {}).get("name", style)
            prompt = f"Young person in {style_name} style, dynamic head-turn, cinematic rim light"
            
            payload = {
                "model": "Qubico/wanx",
                "task_type": "img2video-14b-lora",
                "input": {
                    "init_image": img_url,
                    "prompt": prompt,
                    "lora_settings": {
                        "lora_type": lora_type,
                        "lora_strength": 0.7
                    },
                    "fps": 20,
                    "max_seconds": 6
                }
            }
            
            # Create task
            task_id = await self._create_task(payload)
            if not task_id:
                return None
            
            # Wait for completion
            video_url = await self._wait_for_completion(task_id)
            
            logger.info(f"Short video generated: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"Error generating short video: {e}")
            return None
    
    async def make_long_video(self, img_url: str, style: str, brief: Dict[str, Any], seconds: int = 10) -> Optional[str]:
        """
        Generate long video using Framepack
        Based on section 21.2 of the plan
        """
        
        try:
            # Get style code for LoRA
            from .prompts import PromptGenerator
            prompt_gen = PromptGenerator()
            lora_type = prompt_gen.get_style_code(style)
            
            # Build prompt
            style_name = prompt_gen.style_templates.get(style, {}).get("name", style)
            prompt = f"Young person in {style_name} style, cinematic sequence, dynamic movement"
            
            payload = {
                "model": "Qubico/framepack",
                "task_type": "img2video",
                "input": {
                    "init_image": img_url,
                    "prompt": prompt,
                    "lora_settings": {
                        "lora_type": lora_type,
                        "lora_strength": 0.7
                    },
                    "fps": 15,
                    "max_seconds": min(seconds, 20)  # Max 20 seconds
                }
            }
            
            # Create task
            task_id = await self._create_task(payload)
            if not task_id:
                return None
            
            # Wait for completion (longer timeout for long videos)
            video_url = await self._wait_for_completion(task_id, timeout=300)
            
            logger.info(f"Long video generated: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"Error generating long video: {e}")
            return None
    
    async def _create_task(self, payload: Dict[str, Any]) -> Optional[str]:
        """Create video generation task"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/tasks",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        task_id = data.get("task_id")
                        logger.info(f"Video task created: {task_id}")
                        return task_id
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create video task: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating video task: {e}")
            return None
    
    async def _wait_for_completion(self, task_id: str, timeout: int = 180) -> Optional[str]:
        """Wait for video generation completion"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            start_time = asyncio.get_event_loop().time()
            
            async with aiohttp.ClientSession() as session:
                while True:
                    # Check timeout
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        logger.error(f"Video generation timeout for task {task_id}")
                        return None
                    
                    # Check task status
                    async with session.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=headers
                    ) as response:
                        
                        if response.status != 200:
                            logger.error(f"Failed to check video task status: {response.status}")
                            return None
                        
                        data = await response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            output = data.get("output", {})
                            video_url = output.get("video_url")
                            
                            if video_url:
                                logger.info(f"Video completed: {video_url}")
                                return video_url
                            else:
                                logger.error("Video completed but no URL found")
                                return None
                                
                        elif status == "failed":
                            error = data.get("error", "Unknown error")
                            logger.error(f"Video generation failed: {error}")
                            return None
                        
                        elif status in ["queued", "processing"]:
                            # Wait before next check
                            await asyncio.sleep(10)
                        
                        else:
                            logger.error(f"Unknown video task status: {status}")
                            return None
                            
        except Exception as e:
            logger.error(f"Error waiting for video completion: {e}")
            return None
    
    def get_video_cost(self, package_type: str, video_type: str = "short") -> float:
        """Get video generation cost in USD"""
        
        costs = {
            "short": 0.28,  # WanX short video
            "long": 0.03    # Framepack per second (base rate)
        }
        
        if video_type == "short":
            return costs["short"]
        elif video_type == "long":
            # Assume 10 seconds for long video
            return costs["long"] * 10
        
        return 0.0
    
    def should_generate_video(self, package_type: str) -> bool:
        """Check if package includes video generation"""
        
        return package_type in ["standard", "premium"]
    
    def get_video_count(self, package_type: str) -> int:
        """Get number of videos for package type"""
        
        video_counts = {
            "trial": 0,
            "basic": 0,
            "standard": 1,  # 1 short video
            "premium": 2    # 2 videos (short + long or 2 short)
        }
        
        return video_counts.get(package_type, 0) 