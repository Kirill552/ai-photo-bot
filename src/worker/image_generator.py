"""
Image generation module using PiAPI
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
import httpx
import json
from urllib.parse import urljoin
from .config import settings

logger = logging.getLogger(__name__)


class FluxImageGenerator:
    """Генератор изображений через PiAPI Flux"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.piapi.ai/api/v1"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
    async def generate_image(self, prompt: str, lora_type: str = "mjv6", 
                           width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        """
        Создает задачу генерации изображения через Flux
        
        Args:
            prompt: текст для генерации
            lora_type: тип LoRA модели (mjv6, realism, graphic-portrait)
            width: ширина изображения
            height: высота изображения
            
        Returns:
            Dict с task_id и статусом
        """
        
        payload = {
            "model": "Qubico/flux1-dev-advanced",
            "task_type": "txt2img-lora",
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "guidance_scale": 3.5,
                "steps": 28,
                "lora_settings": [
                    {
                        "lora_type": lora_type,
                        "lora_strength": 1.0
                    }
                ]
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/task",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 200:
                        task_id = result["data"]["task_id"]
                        logger.info(f"✅ Flux task created: {task_id}")
                        return {
                            "success": True,
                            "task_id": task_id,
                            "model": "flux"
                        }
                    else:
                        logger.error(f"❌ Flux API error: {result.get('message', 'Unknown error')}")
                        return {"success": False, "error": result.get("message", "Unknown error")}
                else:
                    logger.error(f"❌ HTTP error: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Flux generation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Получает результат задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Dict с результатом или статусом
        """
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/task/{task_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 200:
                        data = result["data"]
                        status = data.get("status", "").lower()
                        
                        if status == "completed":
                            output = data.get("output", {})
                            image_url = output.get("image_url")
                            if image_url:
                                return {
                                    "success": True,
                                    "completed": True,
                                    "image_url": image_url
                                }
                            else:
                                return {"success": False, "error": "No image URL in response"}
                        elif status in ["pending", "processing"]:
                            return {"success": True, "completed": False, "status": status}
                        elif status == "failed":
                            error_msg = data.get("error", {}).get("message", "Generation failed")
                            return {"success": False, "error": error_msg}
                        else:
                            return {"success": True, "completed": False, "status": status}
                    else:
                        return {"success": False, "error": result.get("message", "API error")}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Get task result error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def wait_for_completion(self, task_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        Ожидает завершения задачи
        
        Args:
            task_id: ID задачи
            max_wait: максимальное время ожидания в секундах
            
        Returns:
            Dict с результатом
        """
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = await self.get_task_result(task_id)
            
            if not result["success"]:
                return result
            
            if result.get("completed"):
                return result
            
            # Ждем перед следующей проверкой
            await asyncio.sleep(5)
        
        return {"success": False, "error": "Timeout waiting for completion"}


class GPTImageGenerator:
    """Генератор изображений через GPT-4o-image"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.piapi.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(self, prompt: str, reference_image: str = None) -> Dict[str, Any]:
        """
        Создает изображение через GPT-4o-image
        
        Args:
            prompt: текст для генерации
            reference_image: URL референсного изображения (опционально)
            
        Returns:
            Dict с результатом
        """
        
        # Формируем контент для сообщения
        content = []
        
        # Добавляем референсное изображение если есть
        if reference_image:
            content.append({
                "type": "image_url",
                "image_url": {"url": reference_image}
            })
        
        # Добавляем текст
        content.append({
            "type": "text",
            "text": prompt
        })
        
        payload = {
            "model": "gpt-4o-image",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "stream": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    
                    if response.status_code != 200:
                        logger.error(f"❌ GPT-4o HTTP error: {response.status_code}")
                        return {"success": False, "error": f"HTTP {response.status_code}"}
                    
                    image_url = None
                    
                    # Парсим stream response
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Убираем "data: "
                            
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content_item = delta.get("content")
                                    
                                    if content_item and isinstance(content_item, list):
                                        for item in content_item:
                                            if item.get("type") == "image_url":
                                                image_url = item.get("image_url", {}).get("url")
                                                break
                                        
                                        if image_url:
                                            break
                                            
                            except json.JSONDecodeError:
                                continue
                    
                    if image_url:
                        logger.info(f"✅ GPT-4o image generated")
                        return {
                            "success": True,
                            "image_url": image_url,
                            "model": "gpt-4o"
                        }
                    else:
                        return {"success": False, "error": "No image URL in response"}
                        
        except Exception as e:
            logger.error(f"❌ GPT-4o generation error: {str(e)}")
            return {"success": False, "error": str(e)}


class ImageGeneratorFactory:
    """Фабрика для создания генераторов изображений"""
    
    @staticmethod
    def create_generator(generator_type: str, api_key: str):
        """
        Создает генератор по типу
        
        Args:
            generator_type: тип генератора (flux, gpt)
            api_key: API ключ
            
        Returns:
            Экземпляр генератора
        """
        
        if generator_type == "flux":
            return FluxImageGenerator(api_key)
        elif generator_type == "gpt":
            return GPTImageGenerator(api_key)
        else:
            raise ValueError(f"Unknown generator type: {generator_type}")


# Sync wrapper для Celery
class SyncImageGenerator:
    """Синхронная обертка для генераторов"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.api_key = settings.PIAPI_KEY
    
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Синхронная генерация изображения"""
        
        generator = ImageGeneratorFactory.create_generator(self.generator_type, self.api_key)
        
        if self.generator_type == "flux":
            # Для Flux создаем задачу и ждем результат
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Создаем задачу
                lora_type = kwargs.get("lora_type", "mjv6")
                width = kwargs.get("width", 1024)
                height = kwargs.get("height", 1024)
                
                task_result = loop.run_until_complete(
                    generator.generate_image(prompt, lora_type, width, height)
                )
                
                if not task_result["success"]:
                    return task_result
                
                # Ждем завершения
                task_id = task_result["task_id"]
                final_result = loop.run_until_complete(
                    generator.wait_for_completion(task_id)
                )
                
                return final_result
                
            finally:
                loop.close()
                
        elif self.generator_type == "gpt":
            # Для GPT прямая генерация
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                reference_image = kwargs.get("reference_image")
                result = loop.run_until_complete(
                    generator.generate_image(prompt, reference_image)
                )
                return result
                
            finally:
                loop.close()
                
        else:
            return {"success": False, "error": f"Unknown generator: {self.generator_type}"}


class ImageGenerator:
    """Image generator using PiAPI"""
    
    def __init__(self, piapi_key: str, openai_key: str):
        self.piapi_key = piapi_key
        self.openai_key = openai_key
        self.piapi_base_url = "https://api.piapi.ai/v1"
        self.timeout = httpx.Timeout(60.0)
        
    def generate_with_flux(
        self,
        prompt: str,
        reference_images: List[str] = None,
        lora_type: str = "realism",
        num_images: int = 4
    ) -> List[str]:
        """Generate images using Flux model"""
        
        try:
            # Prepare request data
            data = {
                "model": "flux-schnell",
                "prompt": prompt,
                "num_images": num_images,
                "size": "1024x1024",
                "quality": "hd",
                "style": lora_type,
                "response_format": "url"
            }
            
            # Add reference images if provided
            if reference_images:
                data["reference_images"] = reference_images[:5]  # Limit to 5 reference images
            
            # Make API request
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    urljoin(self.piapi_base_url, "/images/generations"),
                    json=data,
                    headers={
                        "Authorization": f"Bearer {self.piapi_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract image URLs
                image_urls = []
                for image_data in result.get("data", []):
                    if "url" in image_data:
                        image_urls.append(image_data["url"])
                
                logger.info(f"Generated {len(image_urls)} images with Flux")
                return image_urls
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in Flux generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in Flux generation: {e}")
            raise
    
    def generate_with_gpt(
        self,
        prompt: str,
        reference_images: List[str] = None,
        num_images: int = 4
    ) -> List[str]:
        """Generate images using GPT-4o-image model"""
        
        try:
            # Prepare request data for GPT-4o image generation
            data = {
                "model": "gpt-4o-image",
                "prompt": prompt,
                "num_images": num_images,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "url"
            }
            
            # Add reference images if provided
            if reference_images:
                data["reference_images"] = reference_images[:3]  # Limit for GPT
            
            # Make API request to PiAPI
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    urljoin(self.piapi_base_url, "/images/generations"),
                    json=data,
                    headers={
                        "Authorization": f"Bearer {self.piapi_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract image URLs
                image_urls = []
                for image_data in result.get("data", []):
                    if "url" in image_data:
                        image_urls.append(image_data["url"])
                
                logger.info(f"Generated {len(image_urls)} images with GPT-4o")
                return image_urls
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in GPT generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in GPT generation: {e}")
            raise
    
    def check_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Check generation status (for async jobs)"""
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    urljoin(self.piapi_base_url, f"/jobs/{job_id}"),
                    headers={
                        "Authorization": f"Bearer {self.piapi_key}"
                    }
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error checking job status: {e}")
            raise
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            raise
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from PiAPI"""
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    urljoin(self.piapi_base_url, "/models"),
                    headers={
                        "Authorization": f"Bearer {self.piapi_key}"
                    }
                )
                
                response.raise_for_status()
                return response.json().get("data", [])
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting models: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            raise


class AsyncImageGenerator:
    """Async version of ImageGenerator"""
    
    def __init__(self, piapi_key: str, openai_key: str):
        self.piapi_key = piapi_key
        self.openai_key = openai_key
        self.piapi_base_url = "https://api.piapi.ai/v1"
        self.timeout = httpx.Timeout(60.0)
    
    async def generate_with_flux(
        self,
        prompt: str,
        reference_images: List[str] = None,
        lora_type: str = "realism",
        num_images: int = 4
    ) -> List[str]:
        """Generate images using Flux model (async)"""
        
        try:
            # Prepare request data
            data = {
                "model": "flux-schnell",
                "prompt": prompt,
                "num_images": num_images,
                "size": "1024x1024",
                "quality": "hd",
                "style": lora_type,
                "response_format": "url"
            }
            
            # Add reference images if provided
            if reference_images:
                data["reference_images"] = reference_images[:5]
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    urljoin(self.piapi_base_url, "/images/generations"),
                    json=data,
                    headers={
                        "Authorization": f"Bearer {self.piapi_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract image URLs
                image_urls = []
                for image_data in result.get("data", []):
                    if "url" in image_data:
                        image_urls.append(image_data["url"])
                
                logger.info(f"Generated {len(image_urls)} images with Flux (async)")
                return image_urls
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in async Flux generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in async Flux generation: {e}")
            raise
    
    async def generate_with_gpt(
        self,
        prompt: str,
        reference_images: List[str] = None,
        num_images: int = 4
    ) -> List[str]:
        """Generate images using GPT-4o-image model (async)"""
        
        try:
            # Prepare request data
            data = {
                "model": "gpt-4o-image",
                "prompt": prompt,
                "num_images": num_images,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "url"
            }
            
            # Add reference images if provided
            if reference_images:
                data["reference_images"] = reference_images[:3]
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    urljoin(self.piapi_base_url, "/images/generations"),
                    json=data,
                    headers={
                        "Authorization": f"Bearer {self.piapi_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract image URLs
                image_urls = []
                for image_data in result.get("data", []):
                    if "url" in image_data:
                        image_urls.append(image_data["url"])
                
                logger.info(f"Generated {len(image_urls)} images with GPT-4o (async)")
                return image_urls
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in async GPT generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in async GPT generation: {e}")
            raise
    
    async def batch_generate(
        self,
        prompts: List[str],
        generator_type: str = "flux",
        **kwargs
    ) -> List[str]:
        """Generate multiple images in batch"""
        
        try:
            tasks = []
            for prompt in prompts:
                if generator_type == "flux":
                    task = self.generate_with_flux(prompt, **kwargs)
                else:
                    task = self.generate_with_gpt(prompt, **kwargs)
                tasks.append(task)
            
            # Run tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect all successful results
            all_images = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch generation error: {result}")
                    continue
                all_images.extend(result)
            
            logger.info(f"Batch generated {len(all_images)} images")
            return all_images
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            raise 