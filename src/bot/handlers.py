"""
Message handlers for Telegram Bot
"""

import logging
from typing import Dict, Any, Optional
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .config import Config
from .utils import validate_photo, save_photo, create_session_id
from .assistant import OpenAIAssistant
from .states import PhotoSessionStates

logger = logging.getLogger(__name__)
config = Config()


async def cmd_start(message: Message, state: FSMContext, openai_assistant: OpenAIAssistant):
    """Handle /start command"""
    
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    logger.info(f"User {user_id} (@{username}) started the bot")
    
    # Clear any existing state
    await state.clear()
    
    # Create session
    session_id = create_session_id(user_id)
    await state.update_data(session_id=session_id)
    
    # Welcome message
    welcome_text = f"""
🎭 <b>Добро пожаловать в AI Фотостудию!</b>

Привет, {username}! 

Я помогу тебе создать профессиональные портреты с помощью искусственного интеллекта.

<b>Что я умею:</b>
• Генерировать 40 или 100 студийных фотографий
• Создавать портреты в разных стилях (Vogue, Pastel, CEO и др.)
• Обрабатывать фото за 24 часа
• Выдавать результат в высоком разрешении

<b>Как это работает:</b>
1. Загрузи 10-15 селфи
2. Расскажи о желаемом стиле
3. Получи готовые фото через сутки

Готова начать? Нажми "Начать фотосессию" 👇
"""
    
    # Create inline keyboard
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="✨ Начать фотосессию",
        callback_data="start_session"
    ))
    keyboard.add(InlineKeyboardButton(
        text="📋 Примеры работ",
        callback_data="show_examples"
    ))
    keyboard.add(InlineKeyboardButton(
        text="💰 Цены",
        callback_data="show_prices"
    ))
    keyboard.adjust(1)
    
    await message.answer(welcome_text, reply_markup=keyboard.as_markup())


async def cmd_help(message: Message):
    """Handle /help command"""
    
    help_text = """
🔧 <b>Помощь по боту</b>

<b>Команды:</b>
/start - Начать работу
/new - Новая фотосессия
/status - Статус заказа
/cancel - Отменить заказ

<b>Требования к фото:</b>
• 10-15 селфи разных ракурсов
• Хорошее освещение
• Лицо четко видно
• Размер до 10 МБ каждое

<b>Стили съемки:</b>
• Studio Vogue - глянцевые журнальные фото
• Pastel Dream - нежные пастельные тона
• CEO Shot - деловые портреты
• Film 90s - винтажная пленка
• Golden Hour - золотой час
• Black & White - классика ч/б

<b>Поддержка:</b>
Если возникли вопросы, пиши @support_username
"""
    
    await message.answer(help_text)


async def cmd_new(message: Message, state: FSMContext):
    """Handle /new command"""
    
    # Clear existing state
    await state.clear()
    
    # Create new session
    session_id = create_session_id(message.from_user.id)
    await state.update_data(session_id=session_id)
    
    await message.answer(
        "🆕 Начинаем новую фотосессию!\n\n"
        "Сначала загрузи 10-15 селфи разных ракурсов:",
        reply_markup=get_photo_upload_keyboard()
    )
    
    await state.set_state(PhotoSessionStates.waiting_for_photos)


async def cmd_status(message: Message, state: FSMContext):
    """Handle /status command"""
    
    data = await state.get_data()
    session_id = data.get("session_id")
    
    if not session_id:
        await message.answer("❌ Активной сессии не найдено. Начни новую командой /new")
        return
    
    # TODO: Check session status from database
    await message.answer(
        f"📊 <b>Статус сессии:</b> {session_id}\n\n"
        "🔄 Собираем информацию о твоих предпочтениях...\n"
        "Продолжи диалог, чтобы я могла начать генерацию фото!"
    )


async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command"""
    
    await state.clear()
    await message.answer(
        "❌ Текущая сессия отменена.\n\n"
        "Чтобы начать новую фотосессию, используй команду /new"
    )


async def callback_start_session(callback: CallbackQuery, state: FSMContext):
    """Handle start session callback"""
    
    await callback.answer()
    
    # Clear existing state
    await state.clear()
    
    # Create new session
    session_id = create_session_id(callback.from_user.id)
    await state.update_data(session_id=session_id)
    
    await callback.message.edit_text(
        "📸 <b>Новая фотосессия</b>\n\n"
        "Отлично! Начнем с загрузки твоих фотографий.\n\n"
        "<b>Требования:</b>\n"
        "• 10-15 селфи разных ракурсов\n"
        "• Хорошее освещение\n"
        "• Лицо четко видно\n"
        "• Без фильтров и масок\n\n"
        "Загружай фото по одному или несколько сразу 👇",
        reply_markup=get_photo_upload_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(PhotoSessionStates.waiting_for_photos)


async def callback_show_examples(callback: CallbackQuery):
    """Handle show examples callback"""
    
    await callback.answer()
    
    examples_text = """
🎨 <b>Примеры наших работ</b>

<b>Studio Vogue</b> - драматичное освещение, как в глянцевых журналах
<b>Pastel Dream</b> - нежные пастельные тона, воздушная атмосфера
<b>CEO Shot</b> - деловые портреты для LinkedIn и резюме
<b>Film 90s</b> - винтажная пленка с теплыми тонами
<b>Golden Hour</b> - естественный свет золотого часа
<b>Black & White</b> - классическая черно-белая фотография

Каждый стиль включает разные ракурсы, позы и настроения!
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="✨ Начать фотосессию",
        callback_data="start_session"
    ))
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_start"
    ))
    
    await callback.message.edit_text(examples_text, reply_markup=keyboard.as_markup(), parse_mode="HTML")


async def callback_show_prices(callback: CallbackQuery):
    """Handle show prices callback"""
    
    await callback.answer()
    
    prices_text = """
💰 <b>Наши тарифы (обновлено 2025)</b>

🆓 <b>Пакет "Пробный"</b> - БЕСПЛАТНО
• 2 фото, 1 образ
• Тест качества
• Готовность < 1 час

💫 <b>Пакет "Базовый"</b> - 1 500 ₽
• 10 фото, 3 образа
• Web-качество (1920px)
• Готовность за 6 часов

⭐ <b>Пакет "Стандарт"</b> - 3 500 ₽
• 25 фото, 5 образов + 1 видео
• HQ качество (3K)
• Приоритетная очередь
• Готовность за 24 часа

👑 <b>Пакет "Премиум"</b> - 8 990 ₽
• 50 фото, 8 образов, 2 видео
• 4K + ручная ретушь 5 лучших
• Персональный менеджер
• Права на коммерческое использование
• Готовность за 48 часов

<b>🎁 Бонусы:</b>
• -10% за согласие на портфолио
• 15% кэшбэк за каждую подругу
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="🆓 Попробовать бесплатно",
        callback_data="select_trial"
    ))
    keyboard.add(InlineKeyboardButton(
        text="💫 Базовый - 1500₽",
        callback_data="select_basic"
    ))
    keyboard.add(InlineKeyboardButton(
        text="⭐ Стандарт - 3500₽",
        callback_data="select_standard"
    ))
    keyboard.add(InlineKeyboardButton(
        text="👑 Премиум - 8990₽",
        callback_data="select_premium"
    ))
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_start"
    ))
    keyboard.adjust(1)
    
    await callback.message.edit_text(prices_text, reply_markup=keyboard.as_markup(), parse_mode="HTML")


async def callback_select_package(callback: CallbackQuery, state: FSMContext):
    """Handle package selection"""
    
    await callback.answer()
    
    package_type = callback.data.split("_")[1]  # select_trial -> trial
    
    # Import here to avoid circular imports
    from ..worker.prompts import PromptGenerator
    prompt_gen = PromptGenerator()
    package_info = prompt_gen.get_package_info(package_type)
    
    await state.update_data(
        package_type=package_type,
        package_info=package_info
    )
    
    confirmation_text = f"""
✅ <b>Выбран пакет "{package_info['name']}"</b>

📋 <b>Что включено:</b>
• {package_info['photos']} фотографий
• {package_info['styles']} стилей съемки
{"• 1 короткое видео" if package_info['video'] else ""}
{"• Автоматическая ретушь + 4K upscale" if package_info['post_process'] else ""}

💰 <b>Стоимость:</b> {package_info['price']} ₽

Готова продолжить? Загрузи 10-15 селфи для начала работы!
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="📸 Загрузить фото",
        callback_data="start_photo_upload"
    ))
    keyboard.add(InlineKeyboardButton(
        text="🎨 Посмотреть стили",
        callback_data="show_new_styles"
    ))
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Выбрать другой пакет",
        callback_data="show_prices"
    ))
    keyboard.adjust(1)
    
    await callback.message.edit_text(confirmation_text, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    await state.set_state(PhotoSessionStates.package_selection)


async def callback_show_new_styles(callback: CallbackQuery):
    """Show new styles with previews"""
    
    await callback.answer()
    
    styles_text = """
🎨 <b>Новые стили 2025</b>

⭐ <b>Популярные:</b>
• <b>RL-01</b> - Realistic Studio Vogue
• <b>FN-02</b> - Fantasy Ethereal  
• <b>CEO-05</b> - Corporate Headshot
• <b>PST-06</b> - Pastel Dream

🔥 <b>Эксклюзивные:</b>
• <b>CP-03</b> - Cyberpunk Neon City
• <b>MJ6-04</b> - Midjourney V6 Look
• <b>CLS-07</b> - Classic B&W
• <b>CSP-08</b> - Cosplay Hero

Каждый стиль включает разные образы, освещение и настроения для максимального разнообразия!
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="📸 Начать фотосессию",
        callback_data="start_photo_upload"
    ))
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="show_prices"
    ))
    
    await callback.message.edit_text(styles_text, reply_markup=keyboard.as_markup(), parse_mode="HTML")


async def callback_start_photo_upload(callback: CallbackQuery, state: FSMContext):
    """Start photo upload process"""
    
    await callback.answer()
    
    # Create new session
    from .utils import create_session_id
    session_id = create_session_id(callback.from_user.id)
    await state.update_data(session_id=session_id)
    
    upload_text = """
📸 <b>Загрузка фотографий</b>

<b>Требования к селфи:</b>
• 10-15 фото разных ракурсов
• Хорошее освещение (лучше дневной свет)
• Лицо четко видно
• Без фильтров и масок
• Разные выражения лица
• 2-3 разных образа одежды

Загружай фото по одному или несколько сразу ⬇️
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="💡 Советы по селфи",
        callback_data="photo_tips"
    ))
    keyboard.add(InlineKeyboardButton(
        text="❌ Отменить",
        callback_data="cancel_session"
    ))
    
    await callback.message.edit_text(upload_text, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    await state.set_state(PhotoSessionStates.waiting_for_photos)


async def callback_back_to_start(callback: CallbackQuery, state: FSMContext):
    """Handle back to start callback"""
    
    await callback.answer()
    
    # Reset to start state
    await state.clear()
    
    # Show start message
    await cmd_start(callback.message, state, None)


async def handle_photo(message: Message, state: FSMContext):
    """Handle photo upload"""
    
    current_state = await state.get_state()
    
    if current_state != PhotoSessionStates.waiting_for_photos:
        await message.answer(
            "❌ Сначала начни новую фотосессию командой /new"
        )
        return
    
    data = await state.get_data()
    photos = data.get("photos", [])
    
    # Validate photo
    if not validate_photo(message.photo[-1]):
        await message.answer(
            "❌ Фото не подходит. Проверь, что:\n"
            "• Лицо четко видно\n"
            "• Хорошее освещение\n"
            "• Размер до 10 МБ"
        )
        return
    
    # Save photo
    photo_path = await save_photo(message.photo[-1], data["session_id"])
    photos.append(photo_path)
    
    await state.update_data(photos=photos)
    
    # Check if we have enough photos
    if len(photos) >= 10:
        await message.answer(
            f"✅ Отлично! Загружено {len(photos)} фото.\n\n"
            "Теперь расскажи мне о своих предпочтениях для фотосессии:",
            reply_markup=get_brief_keyboard()
        )
        await state.set_state(PhotoSessionStates.collecting_brief)
    else:
        remaining = 10 - len(photos)
        await message.answer(
            f"📸 Фото {len(photos)}/10 загружено!\n"
            f"Загрузи еще {remaining} фото для продолжения."
        )


async def handle_text(message: Message, state: FSMContext, openai_assistant: OpenAIAssistant):
    """Handle text messages"""
    
    current_state = await state.get_state()
    
    if current_state == PhotoSessionStates.collecting_brief:
        # Forward to OpenAI Assistant
        try:
            response = await openai_assistant.handle_message(
                user_id=message.from_user.id,
                message=message.text,
                state=state
            )
            
            if response:
                await message.answer(response)
        
        except Exception as e:
            logger.error(f"Error handling message with assistant: {e}")
            await message.answer(
                "❌ Произошла ошибка. Попробуй еще раз или начни новую сессию командой /new"
            )
    else:
        await message.answer(
            "❓ Не понимаю. Используй команды:\n"
            "/start - начать работу\n"
            "/new - новая фотосессия\n"
            "/help - помощь"
        )


def get_photo_upload_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for photo upload"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="📱 Как сделать хорошие селфи",
        callback_data="photo_tips"
    ))
    keyboard.add(InlineKeyboardButton(
        text="❌ Отменить",
        callback_data="cancel_session"
    ))
    
    return keyboard.as_markup()


def get_brief_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for brief collection"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="🎨 Посмотреть стили",
        callback_data="show_styles"
    ))
    keyboard.add(InlineKeyboardButton(
        text="💰 Выбрать пакет",
        callback_data="choose_package"
    ))
    
    return keyboard.as_markup()


def setup_handlers(dp: Dispatcher):
    """Setup all handlers"""
    
    # Commands
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_new, Command("new"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_cancel, Command("cancel"))
    
    # Callbacks - Main menu
    dp.callback_query.register(callback_start_session, F.data == "start_session")
    dp.callback_query.register(callback_show_examples, F.data == "show_examples")
    dp.callback_query.register(callback_show_prices, F.data == "show_prices")
    dp.callback_query.register(callback_back_to_start, F.data == "back_to_start")
    
    # Callbacks - Package selection
    dp.callback_query.register(callback_select_package, F.data == "select_trial")
    dp.callback_query.register(callback_select_package, F.data == "select_basic")
    dp.callback_query.register(callback_select_package, F.data == "select_standard")
    dp.callback_query.register(callback_select_package, F.data == "select_premium")
    
    # Callbacks - Styles and upload
    dp.callback_query.register(callback_show_new_styles, F.data == "show_new_styles")
    dp.callback_query.register(callback_start_photo_upload, F.data == "start_photo_upload")
    
    # Content
    dp.message.register(handle_photo, F.content_type == ContentType.PHOTO)
    dp.message.register(handle_text, F.content_type == ContentType.TEXT)
    
    logger.info("Handlers setup completed") 