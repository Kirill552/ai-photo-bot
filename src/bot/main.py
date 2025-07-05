#!/usr/bin/env python3
"""
Telegram Bot для AI фотосессий
"""

import asyncio
import logging
import os
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from .handlers import setup_handlers
from .middleware import OpenAIMiddleware
from .utils import setup_logging, create_temp_dir
from .config import Config
from .states import PhotoSessionStates

# Load environment variables
load_dotenv()

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Configuration
config = Config()


async def create_bot() -> Bot:
    """Create and configure bot instance"""
    
    # Use proxy if configured
    session = None
    if config.PROXY_URL:
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(config.PROXY_URL)
        )
    
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        parse_mode="HTML"
    )
    
    return bot


async def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher"""
    
    # Use memory storage for FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Add middleware
    dp.message.middleware(OpenAIMiddleware())
    dp.callback_query.middleware(OpenAIMiddleware())
    
    # Setup handlers
    setup_handlers(dp)
    
    return dp


async def on_startup(bot: Bot):
    """On startup callback"""
    logger.info("Bot starting up...")
    
    # Create temp directory for files
    create_temp_dir()
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")
    
    # Set bot commands
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="new", description="Новая фотосессия"),
        BotCommand(command="status", description="Статус заказа"),
        BotCommand(command="cancel", description="Отменить заказ"),
    ])


async def on_shutdown(bot: Bot):
    """On shutdown callback"""
    logger.info("Bot shutting down...")
    await bot.session.close()


async def main():
    """Main function"""
    try:
        # Create bot and dispatcher
        bot = await create_bot()
        dp = await create_dispatcher()
        
        # Set startup and shutdown callbacks
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1) 