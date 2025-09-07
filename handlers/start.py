from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db_manager import db_manager
from keyboards.inline import get_main_menu_keyboard, get_analytics_keyboard
from keyboards.reply import get_main_reply_keyboard
from config import config, logger
from messages import messages

# Импортируем функции для меню из других файлов
from handlers.diary import show_diary_menu
from handlers.tags import show_tags_menu
from handlers.settings import show_settings_menu

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

@router.callback_query(F.data == "mood_record")
async def callback_mood_record_from_main(callback: CallbackQuery, state: FSMContext):
    """Обработчик callback кнопки записи настроения из главного меню"""
    try:
        logger.info(f"Callback mood_record received from main menu by user {callback.from_user.id}")
        await callback.answer()

        # Создаем message-like объект для совместимости
        class MockMessage:
            """Mock message object для совместимости между callback и message handlers"""
            def __init__(self, callback):
                self.from_user = callback.from_user
                self.chat = callback.message.chat
                self.bot = callback.bot

            async def answer(self, text, reply_markup=None, parse_mode=None, **kwargs):
                """Mock answer method для отправки сообщений"""
                try:
                    await self.bot.send_message(
                        chat_id=self.chat.id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode,
                        **kwargs
                    )
                    logger.debug(f"MockMessage answer sent to user {self.from_user.id}")
                except Exception as e:
                    logger.error(f"Failed to send MockMessage answer: {e}")
                    raise

        # Импортируем функцию из mood.py
        from handlers.mood import cmd_mood
        mock_message = MockMessage(callback)
        await cmd_mood(mock_message, state)
        logger.info(f"Successfully processed mood_record from main menu for user {callback.from_user.id}")

    except Exception as e:
        logger.error(f"Error in mood_record from main menu callback: {e}")
        await callback.answer("Произошла ошибка при обработке запроса")

@router.callback_query(F.data == "analytics_menu")
async def callback_analytics_menu(callback: CallbackQuery):
    """Обработчик callback кнопки Аналитика"""
    try:
        logger.info(f"Callback analytics_menu received from user {callback.from_user.id}")
        await callback.answer()

        # Проверяем, есть ли записи для анализа
        user_id = callback.from_user.id
        entries = db_manager.get_mood_entries(user_id, limit=1)

        if not entries:
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="📊 У вас пока нет данных для анализа.\n\nНачните с создания записей настроения!",
                reply_markup=get_main_menu_keyboard()
            )
            return

        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text="📈 Аналитика настроения\n\nВыберите тип анализа:",
            reply_markup=get_analytics_keyboard()
        )
        logger.info(f"Successfully showed analytics menu for user {callback.from_user.id}")

    except Exception as e:
        logger.error(f"Error in analytics_menu callback: {e}")
        await callback.answer("Произошла ошибка при открытии аналитики")

@router.callback_query(F.data == "diary_menu")
async def callback_diary_menu(callback: CallbackQuery):
    """Обработчик callback кнопки Дневник"""
    try:
        logger.info(f"Callback diary_menu received from user {callback.from_user.id}")
        await callback.answer()

        # Создаем MockMessage для совместимости с функцией show_diary_menu
        class MockMessage:
            def __init__(self, callback):
                self.from_user = callback.from_user
                self.chat = callback.message.chat
                self.bot = callback.bot

            async def answer(self, text, reply_markup=None, parse_mode=None, **kwargs):
                await self.bot.send_message(
                    chat_id=self.chat.id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                    **kwargs
                )

        mock_message = MockMessage(callback)
        await show_diary_menu(mock_message)
        logger.info(f"Successfully showed diary menu for user {callback.from_user.id}")

    except Exception as e:
        logger.error(f"Error in diary_menu callback: {e}")
        await callback.answer("Произошла ошибка при открытии дневника")

@router.callback_query(F.data == "tags_menu")
async def callback_tags_menu(callback: CallbackQuery):
    """Обработчик callback кнопки Мои теги"""
    try:
        logger.info(f"Callback tags_menu received from user {callback.from_user.id}")
        await callback.answer()

        # Создаем MockMessage для совместимости с функцией show_tags_menu
        class MockMessage:
            def __init__(self, callback):
                self.from_user = callback.from_user
                self.chat = callback.message.chat
                self.bot = callback.bot

            async def answer(self, text, reply_markup=None, parse_mode=None, **kwargs):
                await self.bot.send_message(
                    chat_id=self.chat.id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                    **kwargs
                )

        mock_message = MockMessage(callback)
        await show_tags_menu(mock_message)
        logger.info(f"Successfully showed tags menu for user {callback.from_user.id}")

    except Exception as e:
        logger.error(f"Error in tags_menu callback: {e}")
        await callback.answer("Произошла ошибка при открытии тегов")

@router.callback_query(F.data == "settings_menu")
async def callback_settings_menu(callback: CallbackQuery):
    """Обработчик callback кнопки Настройки"""
    try:
        logger.info(f"Callback settings_menu received from user {callback.from_user.id}")
        await callback.answer()

        # Создаем MockMessage для совместимости с функцией show_settings_menu
        class MockMessage:
            def __init__(self, callback):
                self.from_user = callback.from_user
                self.chat = callback.message.chat
                self.bot = callback.bot

            async def answer(self, text, reply_markup=None, parse_mode=None, **kwargs):
                await self.bot.send_message(
                    chat_id=self.chat.id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                    **kwargs
                )

        mock_message = MockMessage(callback)
        await show_settings_menu(mock_message)
        logger.info(f"Successfully showed settings menu for user {callback.from_user.id}")

    except Exception as e:
        logger.error(f"Error in settings_menu callback: {e}")
        await callback.answer("Произошла ошибка при открытии настроек")
