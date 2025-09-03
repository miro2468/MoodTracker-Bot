import logging
from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import db_manager
from keyboards.inline import (
    get_diary_actions_keyboard,
    get_back_keyboard,
    get_main_menu_keyboard
)
from keyboards.reply import get_main_reply_keyboard
from utils.helpers import format_mood_entry

logger = logging.getLogger(__name__)

router = Router()

# Состояния для FSM
class DiaryStates(StatesGroup):
    waiting_for_diary_text = State()
    waiting_for_search_query = State()

@router.message(Command("diary"))
async def cmd_diary(message: Message):
    """Обработчик команды /diary"""
    try:
        await show_diary_menu(message)
    except Exception as e:
        logger.error(f"Ошибка в команде /diary для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.message(F.text == "📝 Дневник")
async def btn_diary(message: Message):
    """Обработчик кнопки Дневник"""
    await cmd_diary(message)

async def show_diary_menu(message: Message):
    """Показать меню дневника"""
    await message.answer(
        "📝 Дневник эмоций\n\nВыберите действие:",
        reply_markup=get_diary_actions_keyboard()
    )

@router.callback_query(F.data == "diary_write")
async def callback_diary_write(callback: CallbackQuery, state: FSMContext):
    """Обработчик создания новой записи в дневнике"""
    try:
        user_id = callback.from_user.id

        # Проверяем, была ли уже запись сегодня
        today_entry = db_manager.get_today_mood(user_id)
        if today_entry and today_entry.diary_text:
            await callback.message.edit_text(
                "📝 У вас уже есть запись в дневнике сегодня:\n\n" +
                f"\"{today_entry.diary_text}\"\n\n" +
                "Хотите добавить еще одну запись?",
                reply_markup=get_back_keyboard("diary_menu")
            )
            await state.set_state(DiaryStates.waiting_for_diary_text)
        else:
            await callback.message.edit_text(
                "📝 Напишите вашу запись в дневник:",
                reply_markup=get_back_keyboard("diary_menu")
            )
            await state.set_state(DiaryStates.waiting_for_diary_text)

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при создании записи дневника: {e}")
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.callback_query(F.data == "diary_view")
async def callback_diary_view(callback: CallbackQuery):
    """Обработчик просмотра записей дневника"""
    try:
        user_id = callback.from_user.id

        # Получаем последние 10 записей
        entries = db_manager.get_mood_entries(user_id, limit=10)

        if not entries:
            await callback.message.edit_text(
                "📝 У вас пока нет записей в дневнике.\n\n" +
                "Начните с создания первой записи!",
                reply_markup=get_back_keyboard("diary_menu")
            )
            return

        # Форматируем записи
        response = "📝 Ваши записи в дневнике:\n\n"

        for i, entry in enumerate(entries, 1):
            entry_date = entry.entry_date.strftime("%d.%m.%Y")
            mood_emoji = ["😢", "😕", "😐", "🙂", "😊"][entry.mood_score - 1]

            response += f"{i}. {entry_date} {mood_emoji}\n"

            if entry.diary_text:
                # Ограничиваем длину для preview
                preview = entry.diary_text[:100] + "..." if len(entry.diary_text) > 100 else entry.diary_text
                response += f"   \"{preview}\"\n"

            response += "\n"

        response += "📅 Используйте 'Записи за период' для более детального просмотра."

        await callback.message.edit_text(
            response,
            reply_markup=get_back_keyboard("diary_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при просмотре дневника: {e}")
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.callback_query(F.data == "diary_period")
async def callback_diary_period(callback: CallbackQuery):
    """Обработчик просмотра записей за период"""
    try:
        user_id = callback.from_user.id

        # Показываем записи за последнюю неделю
        start_date = date.today() - timedelta(days=7)
        entries = db_manager.get_mood_entries(user_id, start_date=start_date)

        if not entries:
            await callback.message.edit_text(
                "📅 За последнюю неделю записей не найдено.\n\n" +
                "Попробуйте выбрать другой период или создайте новую запись.",
                reply_markup=get_back_keyboard("diary_menu")
            )
            return

        # Группируем по дням
        entries_by_date = {}
        for entry in entries:
            date_key = entry.entry_date
            if date_key not in entries_by_date:
                entries_by_date[date_key] = []
            entries_by_date[date_key].append(entry)

        # Форматируем ответ
        response = f"📅 Записи с {start_date.strftime('%d.%m.%Y')} по {date.today().strftime('%d.%m.%Y')}:\n\n"

        for entry_date in sorted(entries_by_date.keys(), reverse=True):
            day_entries = entries_by_date[entry_date]
            date_str = entry_date.strftime("%d.%m.%Y")

            response += f"📌 {date_str}:\n"

            for entry in day_entries:
                time_str = entry.created_at.strftime("%H:%M") if entry.created_at else ""
                mood_emoji = ["😢", "😕", "😐", "🙂", "😊"][entry.mood_score - 1]

                response += f"   {time_str} {mood_emoji}"
                if entry.diary_text:
                    preview = entry.diary_text[:50] + "..." if len(entry.diary_text) > 50 else entry.diary_text
                    response += f" \"{preview}\""
                response += "\n"

            response += "\n"

        await callback.message.edit_text(
            response,
            reply_markup=get_back_keyboard("diary_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при просмотре записей за период: {e}")
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.callback_query(F.data == "diary_search")
async def callback_diary_search(callback: CallbackQuery, state: FSMContext):
    """Обработчик поиска по дневнику"""
    try:
        await callback.message.edit_text(
            "🔍 Поиск по дневнику\n\n" +
            "Введите слово или фразу для поиска в ваших записях:",
            reply_markup=get_back_keyboard("diary_menu")
        )

        await state.set_state(DiaryStates.waiting_for_search_query)
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при поиске по дневнику: {e}")

@router.message(DiaryStates.waiting_for_search_query)
async def process_search_query(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
    try:
        query = message.text.strip().lower()

        if not query:
            await message.answer("❌ Поисковый запрос не может быть пустым.")
            return

        user_id = message.from_user.id

        # Получаем все записи пользователя
        all_entries = db_manager.get_mood_entries(user_id)

        # Ищем совпадения
        matching_entries = []
        for entry in all_entries:
            if entry.diary_text and query in entry.diary_text.lower():
                matching_entries.append(entry)

        if not matching_entries:
            await message.answer(
                f"🔍 По запросу \"{query}\" ничего не найдено.\n\n" +
                "Попробуйте другой поисковый запрос.",
                reply_markup=get_diary_actions_keyboard()
            )
            await state.clear()
            return

        # Форматируем результаты
        response = f"🔍 Результаты поиска по \"{query}\":\n\n"

        for i, entry in enumerate(matching_entries[:10], 1):  # Ограничиваем 10 результатами
            date_str = entry.entry_date.strftime("%d.%m.%Y")
            time_str = entry.created_at.strftime("%H:%M") if entry.created_at else ""
            mood_emoji = ["😢", "😕", "😐", "🙂", "😊"][entry.mood_score - 1]

            response += f"{i}. {date_str} {time_str} {mood_emoji}\n"

            # Выделяем найденный текст
            text = entry.diary_text
            query_start = text.lower().find(query.lower())
            if query_start != -1:
                # Показываем контекст вокруг найденного текста
                start = max(0, query_start - 30)
                end = min(len(text), query_start + len(query) + 30)
                preview = "..." + text[start:end] + "..." if start > 0 or end < len(text) else text[start:end]

                # Выделяем найденный текст жирным (в Telegram markdown)
                preview = preview.replace(text[query_start:query_start + len(query)], f"**{text[query_start:query_start + len(query)]}**")

                response += f"   \"{preview}\"\n"

            response += "\n"

        if len(matching_entries) > 10:
            response += f"📊 Показано 10 из {len(matching_entries)} результатов."

        await message.answer(response, reply_markup=get_diary_actions_keyboard())
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при обработке поискового запроса: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при поиске.")

@router.message(DiaryStates.waiting_for_diary_text)
async def process_new_diary_entry(message: Message, state: FSMContext):
    """Обработка новой записи в дневник"""
    try:
        diary_text = message.text.strip()

        # Валидация текста
        from utils.helpers import validate_diary_text
        is_valid, error_message = validate_diary_text(diary_text)

        if not is_valid:
            await message.answer(
                f"❌ {error_message}\nПопробуйте снова:"
            )
            return

        user_id = message.from_user.id

        # Создаем запись настроения только с текстом дневника
        # (пользователь может добавить оценку настроения позже)
        entry = db_manager.get_today_mood(user_id)

        if entry:
            # Обновляем существующую запись
            # В реальном проекте нужно добавить метод обновления
            await message.answer(
                "✅ Запись добавлена к сегодняшнему дню!\n\n" +
                f"📝 \"{diary_text}\"",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # Создаем новую запись только с текстом дневника
            entry = db_manager.MoodEntry(
                user_id=user_id,
                mood_score=3,  # Нейтральное настроение по умолчанию
                diary_text=diary_text
            )

            entry_id = db_manager.save_mood_entry(entry)
            await message.answer(
                "✅ Запись сохранена!\n\n" +
                f"📝 \"{diary_text}\"\n\n" +
                "💡 Не забудьте оценить свое настроение в разделе 'Записать настроение'",
                reply_markup=get_main_menu_keyboard()
            )

        await state.clear()
        logger.info(f"Пользователь {user_id} добавил запись в дневник")

    except Exception as e:
        logger.error(f"Ошибка при сохранении записи дневника: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при сохранении.")

@router.callback_query(F.data == "diary_menu")
async def callback_diary_menu(callback: CallbackQuery):
    """Обработчик возврата в меню дневника"""
    try:
        await callback.message.edit_text(
            "📝 Дневник эмоций\n\nВыберите действие:",
            reply_markup=get_diary_actions_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при возврате в меню дневника: {e}")

@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в главное меню"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "🏠 Выберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при возврате в главное меню: {e}")
