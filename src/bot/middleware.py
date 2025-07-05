"""
Middleware for OpenAI Assistant integration
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from .assistant import OpenAIAssistant
from .config import Config

logger = logging.getLogger(__name__)


class OpenAIMiddleware(BaseMiddleware):
    """Middleware для интеграции с OpenAI Assistant"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.assistant = OpenAIAssistant(
            api_key=self.config.OPENAI_API_KEY,
            assistant_id=self.config.ASSISTANT_ID
        )
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Handle middleware call"""
        
        # Add assistant to data
        data["openai_assistant"] = self.assistant
        
        # Log user activity
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            username = event.from_user.username or event.from_user.first_name
            
            if isinstance(event, Message):
                content_type = event.content_type.value
                logger.info(f"User {user_id} (@{username}) sent {content_type}")
            else:
                callback_data = event.data
                logger.info(f"User {user_id} (@{username}) pressed button: {callback_data}")
        
        # Continue with handler
        return await handler(event, data) 