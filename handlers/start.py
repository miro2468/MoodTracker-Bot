from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.db_manager import db_manager
from keyboards.inline import get_main_menu_keyboard
from keyboards.reply import get_main_reply_keyboard
from config import config, logger
from messages import messages

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name

        # Создаем или получаем пользователя
        user = db_manager.get_or_create_user(
            user_id=user_id,
            username=username,
            first_name=first_name
        )

        logger.info(f"Пользователь {user_id} ({username}) начал работу с ботом")

        # Приветственное сообщение
        welcome_text = f"""
🌟 <b>Добро пожаловать в MoodTracker Bot</b>, {first_name or 'друг'}!

{messages.WELCOME_MESSAGE}
"""

        # Отправляем приветствие с клавиатурой
        await message.answer(
            welcome_text,
            reply_markup=get_main_reply_keyboard()
        )

        # Отправляем основное меню
        await message.answer(
            messages.MENU_MAIN,
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка в команде /start для пользователя {message.from_user.id}: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=get_main_reply_keyboard()
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    try:
        await message.answer(
            messages.HELP_COMMAND,
            reply_markup=get_main_reply_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /help для пользователя {message.from_user.id}: {e}")
        await message.answer(messages.ERROR_SERVICE_UNAVAILABLE)

@router.message(F.text == "ℹ️ Помощь")
async def btn_help(message: Message):
    """Обработчик кнопки Помощь"""
    await cmd_help(message)

@router.message(F.text == "🏠 Главное меню")
async def btn_main_menu(message: Message):
    """Обработчик кнопки Главное меню"""
    try:
        await message.answer(
            messages.MENU_MAIN,
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при показе главного меню для пользователя {message.from_user.id}: {e}")
        await message.answer(messages.ERROR_SERVICE_UNAVAILABLE)

@router.message(Command("privacy"))
async def cmd_privacy(message: Message):
    """Обработчик команды /privacy"""
    try:
        privacy_text = """
🔒 Политика приватности

MoodTracker Bot уважает вашу приватность и конфиденциальность данных.

📊 Какие данные мы собираем:
• Оценки вашего настроения (1-5 баллов)
• Текстовые заметки из дневника (опционально)
• Теги для анализа факторов влияния
• Время создания записей

🔐 Как мы защищаем ваши данные:
• Все данные хранятся локально в зашифрованной базе данных
• Доступ к данным имеет только владелец аккаунта
• Мы не передаем данные третьим лицам
• Данные не используются для коммерческих целей

🗑️ Ваши права:
• Вы можете в любой момент удалить все свои данные
• Экспорт данных доступен в формате CSV
• Вы можете отключить напоминания

Если у вас есть вопросы, свяжитесь с разработчиком.
"""
        await message.answer(privacy_text)
    except Exception as e:
        logger.error(f"Ошибка в команде /privacy для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats - быстрая статистика"""
    try:
        user_id = message.from_user.id

        # Получаем статистику за последнюю неделю
        from datetime import date, timedelta
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

        stats = db_manager.get_mood_stats(user_id, start_date, end_date)

        if stats.total_entries == 0:
            await message.answer(
                "📊 У вас пока нет записей настроения.\n"
                "Начните с команды /mood или нажмите '📊 Записать настроение'",
                reply_markup=get_main_menu_keyboard()
            )
            return

        from utils.helpers import format_stats_message
        stats_message = format_stats_message(stats)

        await message.answer(stats_message)

    except Exception as e:
        logger.error(f"Ошибка в команде /stats для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при получении статистики.")
