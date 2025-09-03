import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import db_manager
from database.models import MoodEntry
from keyboards.inline import (
    get_main_menu_keyboard,
    get_mood_rating_keyboard,
    get_tags_selection_keyboard,
    get_back_keyboard,
    get_cancel_keyboard
)
from keyboards.reply import get_mood_quick_reply, get_main_reply_keyboard
from config import config
from utils.helpers import format_mood_entry

logger = logging.getLogger(__name__)

router = Router()

# Состояния для FSM
class MoodStates(StatesGroup):
    waiting_for_mood_rating = State()
    waiting_for_tags_selection = State()
    waiting_for_diary_text = State()

@router.message(Command("mood"))
async def cmd_mood(message: Message, state: FSMContext):
    """Обработчик команды /mood - быстрая запись настроения"""
    try:
        user_id = message.from_user.id

        # Проверяем, была ли уже запись сегодня
        today_entry = db_manager.get_today_mood(user_id)
        if today_entry:
            # Показываем сегодняшнюю запись
            tags = []  # В реальном проекте нужно получить теги для записи
            response = format_mood_entry(today_entry, tags)
            response += "\n\n❓ Хотите обновить запись?"

            await message.answer(
                response,
                reply_markup=get_mood_rating_keyboard()
            )
            return

        # Начинаем процесс записи настроения
        await start_mood_rating(message, state)

    except Exception as e:
        logger.error(f"Ошибка в команде /mood для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.message(F.text == "📊 Записать настроение")
async def btn_mood_record(message: Message, state: FSMContext):
    """Обработчик кнопки записи настроения"""
    await cmd_mood(message, state)

async def start_mood_rating(message: Message, state: FSMContext):
    """Начало процесса оценки настроения"""
    try:
        await state.set_state(MoodStates.waiting_for_mood_rating)

        await message.answer(
            "🌟 Какое у вас настроение сегодня?",
            reply_markup=get_mood_rating_keyboard()
        )

        await message.answer(
            "💡 Или используйте быстрые кнопки:",
            reply_markup=get_mood_quick_reply()
        )

    except Exception as e:
        logger.error(f"Ошибка при начале оценки настроения: {e}")
        await state.clear()

@router.callback_query(F.data.startswith("mood_select_"))
async def callback_mood_select(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора оценки настроения"""
    try:
        mood_score = int(callback.data.split("_")[2])

        if not 1 <= mood_score <= 5:
            await callback.answer("❌ Неверная оценка настроения")
            return

        # Сохраняем оценку в состоянии
        await state.update_data(mood_score=mood_score)

        # Получаем все доступные теги
        user_id = callback.from_user.id
        tags = db_manager.get_all_tags(user_id)

        if not tags:
            # Если тегов нет, сразу переходим к дневнику
            await state.set_state(MoodStates.waiting_for_diary_text)
            await callback.message.edit_text(
                f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n"
                "📝 Напишите заметку для дневника (опционально):",
                reply_markup=get_cancel_keyboard()
            )
        else:
            # Показываем выбор тегов
            await state.set_state(MoodStates.waiting_for_tags_selection)
            await callback.message.edit_text(
                f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n"
                "🏷️ Выберите теги, которые описывают ваше состояние:",
                reply_markup=get_tags_selection_keyboard(tags)
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при выборе оценки настроения: {e}")
        await state.clear()
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.message(MoodStates.waiting_for_mood_rating, F.text)
async def process_mood_quick_reply(message: Message, state: FSMContext):
    """Обработка быстрого ответа на оценку настроения"""
    try:
        text = message.text.strip()

        # Маппинг текста на оценку
        mood_mapping = {
            "😢 Очень плохо": 1,
            "😕 Плохо": 2,
            "😐 Нейтрально": 3,
            "🙂 Хорошо": 4,
            "😊 Отлично": 5
        }

        if text not in mood_mapping:
            await message.answer(
                "❌ Пожалуйста, выберите настроение из предложенных вариантов.",
                reply_markup=get_mood_quick_reply()
            )
            return

        mood_score = mood_mapping[text]
        await state.update_data(mood_score=mood_score)

        # Продолжаем процесс как при выборе из inline клавиатуры
        user_id = message.from_user.id
        tags = db_manager.get_all_tags(user_id)

        if not tags:
            await state.set_state(MoodStates.waiting_for_diary_text)
            await message.answer(
                f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n"
                "📝 Напишите заметку для дневника (опционально):",
                reply_markup=get_cancel_keyboard()
            )
        else:
            await state.set_state(MoodStates.waiting_for_tags_selection)
            await message.answer(
                f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n"
                "🏷️ Выберите теги, которые описывают ваше состояние:",
                reply_markup=get_tags_selection_keyboard(tags)
            )

    except Exception as e:
        logger.error(f"Ошибка при обработке быстрого ответа: {e}")
        await state.clear()

@router.callback_query(F.data.startswith("tag_toggle_"))
async def callback_tag_toggle(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора/отмены выбора тега"""
    try:
        tag_id = int(callback.data.split("_")[2])

        # Получаем текущие выбранные теги
        data = await state.get_data()
        selected_tags = data.get('selected_tags', [])

        if tag_id in selected_tags:
            selected_tags.remove(tag_id)
        else:
            selected_tags.append(tag_id)

        await state.update_data(selected_tags=selected_tags)

        # Обновляем клавиатуру
        user_id = callback.from_user.id
        tags = db_manager.get_all_tags(user_id)

        mood_score = data.get('mood_score')
        mood_text = f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n" if mood_score else ""

        selected_count = len(selected_tags)
        tags_text = f"🏷️ Выберите теги ({selected_count} выбрано):" if selected_count > 0 else "🏷️ Выберите теги:"

        await callback.message.edit_text(
            mood_text + tags_text,
            reply_markup=get_tags_selection_keyboard(tags, selected_tags)
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при выборе тега: {e}")

@router.callback_query(F.data == "tags_done")
async def callback_tags_done(callback: CallbackQuery, state: FSMContext):
    """Обработчик завершения выбора тегов"""
    try:
        await state.set_state(MoodStates.waiting_for_diary_text)

        data = await state.get_data()
        mood_score = data.get('mood_score')
        selected_tags = data.get('selected_tags', [])

        mood_text = f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n" if mood_score else ""
        tags_text = f"Выбрано тегов: {len(selected_tags)}\n\n" if selected_tags else ""

        await callback.message.edit_text(
            mood_text + tags_text + "📝 Напишите заметку для дневника (опционально):",
            reply_markup=get_cancel_keyboard()
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при завершении выбора тегов: {e}")

@router.callback_query(F.data == "tags_reset")
async def callback_tags_reset(callback: CallbackQuery, state: FSMContext):
    """Обработчик сброса выбора тегов"""
    try:
        await state.update_data(selected_tags=[])

        data = await state.get_data()
        user_id = callback.from_user.id
        tags = db_manager.get_all_tags(user_id)
        mood_score = data.get('mood_score')

        mood_text = f"Вы выбрали: {config.MOOD_EMOJIS[mood_score]} {config.MOOD_NAMES[mood_score]}\n\n" if mood_score else ""

        await callback.message.edit_text(
            mood_text + "🏷️ Выберите теги:",
            reply_markup=get_tags_selection_keyboard(tags, [])
        )

        await callback.answer("Выбор тегов сброшен")

    except Exception as e:
        logger.error(f"Ошибка при сбросе выбора тегов: {e}")

@router.message(MoodStates.waiting_for_diary_text)
async def process_diary_text(message: Message, state: FSMContext):
    """Обработка текста дневника"""
    try:
        diary_text = message.text.strip() if message.text != "❌ Отмена" else ""

        # Валидация текста
        from utils.helpers import validate_diary_text
        is_valid, error_message = validate_diary_text(diary_text)

        if not is_valid:
            await message.answer(
                f"❌ {error_message}\nПопробуйте снова или нажмите '❌ Отмена':"
            )
            return

        # Получаем данные из состояния
        data = await state.get_data()
        mood_score = data.get('mood_score')
        selected_tags = data.get('selected_tags', [])

        if not mood_score:
            await message.answer("❌ Ошибка: не указана оценка настроения")
            await state.clear()
            return

        # Создаем запись настроения
        user_id = message.from_user.id
        entry = MoodEntry(
            user_id=user_id,
            mood_score=mood_score,
            diary_text=diary_text if diary_text else None
        )

        # Сохраняем запись
        entry_id = db_manager.save_mood_entry(entry, selected_tags)

        # Получаем теги для отображения
        tags = []
        if selected_tags:
            all_tags = db_manager.get_all_tags(user_id)
            tags = [tag for tag in all_tags if tag.id in selected_tags]

        # Форматируем и отправляем результат
        response = format_mood_entry(entry, tags)
        await message.answer(response, reply_markup=get_main_menu_keyboard())

        # Очищаем состояние
        await state.clear()

        logger.info(f"Пользователь {user_id} сохранил запись настроения {entry_id}")

    except Exception as e:
        logger.error(f"Ошибка при сохранении записи настроения: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при сохранении.")

@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "❌ Действие отменено.",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при отмене: {e}")

@router.message(F.text == "❌ Отмена")
async def message_cancel(message: Message, state: FSMContext):
    """Обработчик отмены через текстовое сообщение"""
    await state.clear()
    await message.answer(
        "❌ Действие отменено.",
        reply_markup=get_main_menu_keyboard()
    )
