import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Настройка уровней логирования для разных модулей
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # Создание логгера для бота
    logger = logging.getLogger('mood_tracker')
    logger.setLevel(logging.INFO)

    return logger

# Глобальный логгер
logger = setup_logging()

class Config:
    """Конфигурация бота"""

    # Токен бота Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    # Настройки базы данных
    DATABASE_PATH = 'mood_tracker.db'

    # Эмодзи для настроений
    MOOD_EMOJIS = {
        1: "😢",
        2: "😕",
        3: "😐",
        4: "🙂",
        5: "😊"
    }

    # Названия настроений
    MOOD_NAMES = {
        1: "Очень плохо",
        2: "Плохо",
        3: "Нейтрально",
        4: "Хорошо",
        5: "Отлично"
    }

    # Предустановленные теги по категориям
    PREDEFINED_TAGS = {
        "Работа/Учеба": ["💼 работа", "📚 учеба", "🎯 проект", "⏰ дедлайн"],
        "Отношения": ["❤️ семья", "👫 друзья", "💕 любовь", "😤 конфликт"],
        "Здоровье": ["💊 болезнь", "🏃 спорт", "😴 сон", "🍎 питание"],
        "Досуг": ["🎬 кино", "📖 чтение", "🎵 музыка", "🎮 игры"],
        "Погода": ["☀️ солнце", "🌧️ дождь", "❄️ снег", "🌈 радуга"],
        "События": ["🎉 праздник", "🎂 день рождения", "✈️ путешествие"]
    }

    # Настройки графиков
    CHART_COLORS = {
        'excellent': '#4CAF50',  # Зеленый
        'good': '#8BC34A',       # Светло-зеленый
        'neutral': '#FFEB3B',    # Желтый
        'bad': '#FF9800',        # Оранжевый
        'terrible': '#F44336'    # Красный
    }

    # Лимиты
    DIARY_TEXT_LIMIT = 500
    MAX_CUSTOM_TAGS = 50

    # Настройки напоминаний
    DEFAULT_REMINDER_TIME = "21:00"
    DEFAULT_TIMEZONE = "UTC+3"

    # Сообщения бота
    WELCOME_MESSAGE = """
🌟 Добро пожаловать в MoodTracker Bot!

Ваш персональный помощник для отслеживания эмоционального благополучия.

Я помогу вам:
📊 Отслеживать настроение каждый день
🏷️ Анализировать факторы влияния с помощью тегов
📝 Вести дневник эмоций
📈 Анализировать тренды и паттерны

Начнем? Нажмите /start или выберите действие из меню ниже.
"""

    HELP_MESSAGE = """
📋 Справка по командам:

/start - Начать работу с ботом
/mood - Быстро записать настроение
/diary - Открыть дневник
/stats - Показать статистику
/tags - Управление тегами
/settings - Настройки
/export - Экспорт данных
/help - Показать эту справку
/privacy - Политика приватности

💡 Советы по использованию:
• Записывайте настроение регулярно для лучших результатов
• Используйте теги для анализа факторов влияния
• Ведите дневник для более глубокого понимания эмоций
"""

config = Config()
