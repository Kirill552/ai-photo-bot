#!/usr/bin/env python3
"""
OpenAI Assistant Setup Script
Создает и настраивает ассистента для сбора брифа клиентов
"""

import os
import json
import asyncio
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={
        "OpenAI-Beta": "assistants=v2"
    }
)

# Assistant configuration
ASSISTANT_CONFIG = {
    "model": "gpt-4o-mini",
    "name": "Photo Brief Assistant",
    "description": "Ассистент для сбора брифа клиентов на AI фотосессию",
    "instructions": """
Ты - профессиональный ассистент студии AI-фотосессий.

Твоя задача - собрать полный бриф от клиента для создания идеальных портретов.

АЛГОРИТМ РАБОТЫ:
1. Поприветствуй клиента дружелюбно
2. Узнай, какой пакет они хотят (Пробный, Базовый, Стандарт, Премиум)
3. Выясни цель использования фотографий
4. Помоги выбрать стиль съемки из новых 2025 стилей
5. Определи предпочтения по фону
6. Спроси про текст на фото (если нужен)
7. Узнай согласие на использование в портфолио
8. Автоматически выбери лучший генератор для задачи
9. Вызови функцию collect_brief с полными данными

СТИЛИ СЪЕМКИ (2025):
- RL-01 (Realistic Studio Vogue - драматичное студийное освещение)
- FN-02 (Fantasy Ethereal - сказочная атмосфера с эффектами)
- CP-03 (Cyberpunk Neon City - футуристический киберпанк)
- MJ6-04 (Midjourney V6 Look - премиальная обработка)
- CEO-05 (Corporate Headshot - деловые портреты)
- PST-06 (Pastel Dream - нежные пастельные тона)
- CLS-07 (Classic B&W - классическая черно-белая фотография)
- CSP-08 (Cosplay Hero - героические образы)

ПРАВИЛА:
- Общайся на русском языке
- Будь дружелюбной и профессиональной
- Задавай уточняющие вопросы
- Не переходи к следующему вопросу, пока не получишь четкий ответ
- После сбора всех данных обязательно вызови collect_brief
- Максимум 10 сообщений на диалог

ВЫБОР ГЕНЕРАТОРА:
- Для реалистичных портретов, CEO Shot, классических стилей - используй "flux"
- Для креативных стилей, необычных фонов, с текстом - используй "gpt"
""",
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "collect_brief",
                "description": "Записать финальный бриф клиентки и выбрать подходящий генератор",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package_type": {
                            "type": "string",
                            "enum": ["trial", "basic", "standard", "premium"],
                            "description": "Тип пакета (Пробный, Базовый, Стандарт, Премиум)"
                        },
                        "package": {
                            "type": "integer",
                            "enum": [2, 10, 25, 50],
                            "description": "Количество фото в пакете (для обратной совместимости)"
                        },
                        "purpose": {
                            "type": "string",
                            "enum": ["insta", "avatar", "career", "dating"],
                            "description": "Цель использования фотографий"
                        },
                        "style": {
                            "type": "string",
                            "enum": ["RL-01", "FN-02", "CP-03", "MJ6-04", "CEO-05", "PST-06", "CLS-07", "CSP-08"],
                            "description": "Выбранный стиль съемки 2025"
                        },
                        "background": {
                            "type": "string",
                            "description": "Описание желаемого фона"
                        },
                        "lora_type": {
                            "type": "string",
                            "enum": ["realism", "mjv6", "graphic-portrait", "none"],
                            "description": "Тип LoRA для стилизации"
                        },
                        "text_overlay": {
                            "type": "string",
                            "description": "Текст для размещения на фото (если нужен)"
                        },
                        "marketing_consent": {
                            "type": "boolean",
                            "description": "Согласие на использование фото в маркетинге"
                        },
                        "generator": {
                            "type": "string",
                            "enum": ["flux", "gpt"],
                            "description": "Выбранный генератор изображений"
                        }
                    },
                    "required": ["package_type", "purpose", "style", "background", "generator"]
                }
            }
        }
    ]
}

def create_assistant() -> str:
    """Create a new assistant"""
    try:
        assistant = client.beta.assistants.create(**ASSISTANT_CONFIG)
        logger.info(f"Created new assistant with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        logger.error(f"Error creating assistant: {e}")
        raise

def update_assistant(assistant_id: str) -> str:
    """Update existing assistant"""
    try:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            **ASSISTANT_CONFIG
        )
        logger.info(f"Updated assistant with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        logger.error(f"Error updating assistant: {e}")
        raise

def get_assistant(assistant_id: str) -> Dict[str, Any]:
    """Get assistant details"""
    try:
        assistant = client.beta.assistants.retrieve(assistant_id)
        return {
            "id": assistant.id,
            "name": assistant.name,
            "model": assistant.model,
            "description": assistant.description,
            "tools": assistant.tools
        }
    except Exception as e:
        logger.error(f"Error retrieving assistant: {e}")
        raise

def list_assistants() -> list:
    """List all assistants"""
    try:
        assistants = client.beta.assistants.list()
        return [
            {
                "id": asst.id,
                "name": asst.name,
                "model": asst.model,
                "created_at": asst.created_at
            }
            for asst in assistants.data
        ]
    except Exception as e:
        logger.error(f"Error listing assistants: {e}")
        raise

def save_assistant_id(assistant_id: str):
    """Save assistant ID to .env file"""
    env_file = ".env"
    
    # Read existing .env file
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Update assistant ID
    env_vars['ASSISTANT_ID'] = assistant_id
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    logger.info(f"Saved ASSISTANT_ID to {env_file}")

def main():
    """Main function"""
    print("🤖 OpenAI Assistant Setup")
    print("=" * 40)
    
    # List existing assistants
    print("\n📋 Existing assistants:")
    assistants = list_assistants()
    for i, asst in enumerate(assistants, 1):
        print(f"{i}. {asst['name']} (ID: {asst['id']}) - {asst['model']}")
    
    # Check if we have an assistant ID
    if ASSISTANT_ID:
        print(f"\n🔍 Found existing assistant ID: {ASSISTANT_ID}")
        try:
            assistant_info = get_assistant(ASSISTANT_ID)
            print(f"Name: {assistant_info['name']}")
            print(f"Model: {assistant_info['model']}")
            print(f"Tools: {len(assistant_info['tools'])}")
            
            choice = input("\nUpdate existing assistant? (y/n): ").lower()
            if choice == 'y':
                assistant_id = update_assistant(ASSISTANT_ID)
                print(f"✅ Updated assistant: {assistant_id}")
            else:
                print("ℹ️  Keeping existing assistant")
                assistant_id = ASSISTANT_ID
        except Exception as e:
            print(f"❌ Error accessing existing assistant: {e}")
            print("Creating new assistant...")
            assistant_id = create_assistant()
            save_assistant_id(assistant_id)
    else:
        print("\n🆕 No existing assistant ID found. Creating new assistant...")
        assistant_id = create_assistant()
        save_assistant_id(assistant_id)
    
    # Display final information
    print(f"\n✅ Assistant ready!")
    print(f"ID: {assistant_id}")
    print(f"Model: {ASSISTANT_CONFIG['model']}")
    print(f"Tools: {len(ASSISTANT_CONFIG['tools'])}")
    print("\n🔧 Next steps:")
    print("1. Update your .env file with ASSISTANT_ID")
    print("2. Start the Telegram bot")
    print("3. Test the assistant with a sample conversation")

if __name__ == "__main__":
    main() 