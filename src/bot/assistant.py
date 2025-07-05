"""
OpenAI Assistant integration
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)


class OpenAIAssistant:
    """Класс для работы с OpenAI Assistant"""
    
    def __init__(self, api_key: str, assistant_id: str, base_url: str = None):
        """Initialize OpenAI Assistant"""
        
        self.assistant_id = assistant_id
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Store user threads
        self.user_threads: Dict[int, str] = {}
        
        logger.info(f"OpenAI Assistant initialized with ID: {assistant_id}")
    
    async def get_or_create_thread(self, user_id: int) -> str:
        """Get or create thread for user"""
        
        if user_id not in self.user_threads:
            try:
                thread = await self.client.threads.create()
                self.user_threads[user_id] = thread.id
                logger.info(f"Created new thread for user {user_id}: {thread.id}")
            except Exception as e:
                logger.error(f"Error creating thread: {e}")
                raise
        
        return self.user_threads[user_id]
    
    async def handle_message(self, user_id: int, message: str, state: FSMContext) -> Optional[str]:
        """Handle message from user"""
        
        try:
            # Get or create thread
            thread_id = await self.get_or_create_thread(user_id)
            
            # Add user message to thread
            await self.client.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # Create and run assistant
            run = await self.client.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                await asyncio.sleep(1)
                run = await self.client.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
            
            # Handle tool calls
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                
                for tool_call in tool_calls:
                    if tool_call.function.name == "collect_brief":
                        # Parse brief data
                        brief_data = json.loads(tool_call.function.arguments)
                        
                        # Save brief to state
                        await state.update_data(brief=brief_data)
                        
                        # Submit tool output
                        await self.client.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run.id,
                            tool_outputs=[{
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"status": "success", "message": "Brief collected"})
                            }]
                        )
                        
                        # Start image generation process
                        await self._start_image_generation(user_id, brief_data, state)
                        
                        return "✅ Отлично! Бриф собран. Начинаю генерацию фотографий..."
            
            # Get assistant response
            elif run.status == "completed":
                messages = await self.client.threads.messages.list(
                    thread_id=thread_id,
                    order="desc",
                    limit=1
                )
                
                if messages.data:
                    return messages.data[0].content[0].text.value
            
            elif run.status == "failed":
                logger.error(f"Assistant run failed: {run.last_error}")
                return "❌ Произошла ошибка. Попробуй еще раз."
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return "❌ Произошла ошибка. Попробуй еще раз."
    
    async def _start_image_generation(self, user_id: int, brief_data: Dict[str, Any], state: FSMContext):
        """Start image generation process"""
        
        try:
            # Import here to avoid circular imports
            from .tasks import generate_images_task
            
            # Get session data
            data = await state.get_data()
            session_id = data.get("session_id")
            photos = data.get("photos", [])
            
            # Create generation task
            task_data = {
                "user_id": user_id,
                "session_id": session_id,
                "brief": brief_data,
                "photos": photos
            }
            
            # Send to task queue
            generate_images_task.delay(task_data)
            
            logger.info(f"Started image generation for user {user_id}, session {session_id}")
            
        except Exception as e:
            logger.error(f"Error starting image generation: {e}")
            raise
    
    async def reset_thread(self, user_id: int):
        """Reset thread for user"""
        
        if user_id in self.user_threads:
            del self.user_threads[user_id]
            logger.info(f"Reset thread for user {user_id}")
    
    async def get_assistant_info(self) -> Dict[str, Any]:
        """Get assistant information"""
        
        try:
            assistant = await self.client.assistants.retrieve(self.assistant_id)
            return {
                "id": assistant.id,
                "name": assistant.name,
                "model": assistant.model,
                "description": assistant.description,
                "tools": len(assistant.tools)
            }
        except Exception as e:
            logger.error(f"Error getting assistant info: {e}")
            raise 