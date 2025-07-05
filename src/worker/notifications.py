"""
Telegram notifications module
"""

import logging
from typing import List
import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram Bot API"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.timeout = httpx.Timeout(30.0)
    
    def send_message(self, user_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Send text message to user"""
        
        try:
            data = {
                "chat_id": user_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    urljoin(self.base_url, "/sendMessage"),
                    json=data
                )
                
                response.raise_for_status()
                logger.info(f"Sent message to user {user_id}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_media_group(self, user_id: int, image_urls: List[str]) -> bool:
        """Send media group to user"""
        
        try:
            # Telegram limits media groups to 10 items
            chunks = [image_urls[i:i+10] for i in range(0, len(image_urls), 10)]
            
            for chunk in chunks:
                media = []
                for i, url in enumerate(chunk):
                    media_item = {
                        "type": "photo",
                        "media": url
                    }
                    if i == 0:  # Add caption to first photo
                        media_item["caption"] = "🎉 Твои фотографии готовы!"
                    
                    media.append(media_item)
                
                data = {
                    "chat_id": user_id,
                    "media": media
                }
                
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        urljoin(self.base_url, "/sendMediaGroup"),
                        json=data
                    )
                    
                    response.raise_for_status()
            
            logger.info(f"Sent {len(image_urls)} images to user {user_id}")
            return True
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending media group: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending media group: {e}")
            return False
    
    def send_document(self, user_id: int, document_url: str, caption: str = "") -> bool:
        """Send document to user"""
        
        try:
            data = {
                "chat_id": user_id,
                "document": document_url,
                "caption": caption
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    urljoin(self.base_url, "/sendDocument"),
                    json=data
                )
                
                response.raise_for_status()
                logger.info(f"Sent document to user {user_id}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending document: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return False 