from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import db_manager
from database.models import Tag
from keyboards.inline import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_confirmation_keyboard
)
from keyboards.reply import get_main_reply_keyboard
from config import logger

router = Router()

# Состояния для FSM
class TagStates(StatesGroup):
    waiting_for_tag_name = State()
    waiting_for_category_name = State()

@router.message(Command("tags"))
async def cmd_tags(message: Message):
    """Обработчик команды /tags"""
    try:
        await show_tags_menu(message)
    except Exception as e:
        logger.error(f"Ошибка в команде /tags для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.message(F.text == "🏷️ Мои теги")
async def btn_tags(message: Message):
    """Обработчик кнопки Мои теги"""
    await cmd_tags(message)

async def show_tags_menu(message: Message):
    """Показать меню управления тегами"""
    try:
        user_id = message.from_user.id

        # Получаем все теги пользователя
        tags = db_manager.get_all_tags(user_id)

        if not tags:
            await message.answer(
                "🏷️ У вас пока нет тегов.\n\n" +
                "Теги помогают анализировать факторы, влияющие на ваше настроение.\n" +
                "Начните с создания первого тега!",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # Группируем теги по категориям
        categories = {}
        for tag in tags:
            category = tag.category or "Другие"
            if category not in categories:
                categories[category] = []
            categories[category].append(tag)

        # Форматируем список тегов
        response = "🏷️ Ваши теги:\n\n"

        for category, category_tags in categories.items():
            response += f"📂 {category}:\n"

            for tag in category_tags:
                status = "✅" if not tag.is_predefined else "🔒"
                response += f"   {status} {tag.name}\n"

            response += "\n"

        response += "💡 Используйте теги при записи настроения для лучшего анализа."

        # Создаем клавиатуру с действиями
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()

        builder.button(text="➕ Создать тег", callback_data="tag_create")
        builder.button(text="🗑️ Удалить тег", callback_data="tag_delete")
        builder.button(text="📊 Статистика", callback_data="tag_stats")

        builder.adjust(2, 1)

        await message.answer(
            response,
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Ошибка при показе меню тегов: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.callback_query(F.data == "tag_create")
async def callback_tag_create(callback: CallbackQuery, state: FSMContext):
    """Обработчик создания нового тега"""
    try:
        await callback.message.edit_text(
            "➕ Создание нового тега\n\n" +
            "Введите название тега (например: 'работа', 'спорт', 'семья'):",
            reply_markup=get_back_keyboard("tags_menu")
        )

        await state.set_state(TagStates.waiting_for_tag_name)
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при создании тега: {e}")

@router.message(TagStates.waiting_for_tag_name)
async def process_tag_name(message: Message, state: FSMContext):
    """Обработка названия тега"""
    try:
        tag_name = message.text.strip()

        if not tag_name:
            await message.answer("❌ Название тега не может быть пустым.")
            return

        if len(tag_name) > 50:
            await message.answer("❌ Название тега слишком длинное (максимум 50 символов).")
            return

        # Проверяем, существует ли уже такой тег
        user_id = message.from_user.id
        existing_tags = db_manager.get_all_tags(user_id)

        if any(tag.name.lower() == tag_name.lower() for tag in existing_tags):
            await message.answer(
                f"❌ Тег '{tag_name}' уже существует.\nПопробуйте другое название:"
            )
            return

        # Сохраняем название тега
        await state.update_data(tag_name=tag_name)

        # Предлагаем выбрать категорию
        await message.answer(
            f"📂 Выберите категорию для тега '{tag_name}':\n\n" +
            "Отправьте название категории или выберите из предложенных:\n" +
            "• Работа/Учеба\n" +
            "• Отношения\n" +
            "• Здоровье\n" +
            "• Досуг\n" +
            "• Погода\n" +
            "• События\n" +
            "• Другое"
        )

        await state.set_state(TagStates.waiting_for_category_name)

    except Exception as e:
        logger.error(f"Ошибка при обработке названия тега: {e}")
        await state.clear()

@router.message(TagStates.waiting_for_category_name)
async def process_category_name(message: Message, state: FSMContext):
    """Обработка названия категории"""
    try:
        category_name = message.text.strip()

        if not category_name:
            await message.answer("❌ Название категории не может быть пустым.")
            return

        # Получаем данные
        data = await state.get_data()
        tag_name = data.get('tag_name')
        user_id = message.from_user.id

        if not tag_name:
            await message.answer("❌ Ошибка: название тега не найдено.")
            await state.clear()
            return

        # Создаем тег
        tag_id = db_manager.create_custom_tag(tag_name, category_name, user_id)

        await message.answer(
            f"✅ Тег успешно создан!\n\n" +
            f"🏷️ {tag_name}\n" +
            f"📂 Категория: {category_name}\n\n" +
            "Теперь вы можете использовать этот тег при записи настроения.",
            reply_markup=get_main_menu_keyboard()
        )

        await state.clear()
        logger.info(f"Пользователь {user_id} создал тег '{tag_name}' в категории '{category_name}'")

    except Exception as e:
        logger.error(f"Ошибка при создании тега: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при создании тега.")

@router.callback_query(F.data == "tag_delete")
async def callback_tag_delete(callback: CallbackQuery):
    """Обработчик удаления тега"""
    try:
        user_id = callback.from_user.id

        # Получаем пользовательские теги
        tags = db_manager.get_all_tags(user_id)
        custom_tags = [tag for tag in tags if not tag.is_predefined]

        if not custom_tags:
            await callback.message.edit_text(
                "🗑️ У вас нет пользовательских тегов для удаления.\n\n" +
                "Только предустановленные теги не могут быть удалены.",
                reply_markup=get_back_keyboard("tags_menu")
            )
            return

        # Создаем клавиатуру с пользовательскими тегами
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()

        for tag in custom_tags:
            builder.button(
                text=f"🗑️ {tag.name}",
                callback_data=f"delete_tag_{tag.id}"
            )

        builder.button(text="⬅️ Назад", callback_data="tags_menu")
        builder.adjust(1)

        await callback.message.edit_text(
            "🗑️ Выберите тег для удаления:\n\n" +
            "⚠️ Предустановленные теги удалить нельзя.",
            reply_markup=builder.as_markup()
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при удалении тега: {e}")

@router.callback_query(F.data.startswith("delete_tag_"))
async def callback_delete_specific_tag(callback: CallbackQuery):
    """Обработчик удаления конкретного тега"""
    try:
        tag_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id

        # Получаем информацию о теге
        tags = db_manager.get_all_tags(user_id)
        tag_to_delete = next((tag for tag in tags if tag.id == tag_id), None)

        if not tag_to_delete:
            await callback.answer("❌ Тег не найден")
            return

        if tag_to_delete.is_predefined:
            await callback.answer("❌ Предустановленный тег нельзя удалить")
            return

        # Показываем подтверждение
        await callback.message.edit_text(
            f"🗑️ Удалить тег '{tag_to_delete.name}'?\n\n" +
            "Это действие нельзя отменить!",
            reply_markup=get_confirmation_keyboard(f"delete_tag_{tag_id}")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при удалении тега: {e}")

@router.callback_query(F.data.startswith("confirm_delete_tag_"))
async def callback_confirm_delete_tag(callback: CallbackQuery):
    """Подтверждение удаления тега"""
    try:
        tag_id = int(callback.data.split("_")[3])
        user_id = callback.from_user.id

        # Удаляем тег
        success = db_manager.delete_custom_tag(tag_id, user_id)

        if success:
            await callback.message.edit_text(
                "✅ Тег успешно удален!",
                reply_markup=get_back_keyboard("tags_menu")
            )
            logger.info(f"Пользователь {user_id} удалил тег {tag_id}")
        else:
            await callback.message.edit_text(
                "❌ Не удалось удалить тег.\nВозможно, он уже был удален.",
                reply_markup=get_back_keyboard("tags_menu")
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при подтверждении удаления тега: {e}")

@router.callback_query(F.data == "tag_stats")
async def callback_tag_stats(callback: CallbackQuery):
    """Обработчик статистики по тегам"""
    try:
        user_id = callback.from_user.id

        # Получаем все записи пользователя
        entries = db_manager.get_mood_entries(user_id)

        if not entries:
            await callback.message.edit_text(
                "📊 Нет данных для анализа тегов.",
                reply_markup=get_back_keyboard("tags_menu")
            )
            return

        # Собираем статистику по тегам
        tags = db_manager.get_all_tags(user_id)
        tag_usage = {}

        for tag in tags:
            usage_count = 0
            # В реальном проекте нужно подсчитать использование тега
            tag_usage[tag.name] = usage_count

        # Форматируем статистику
        response = "📊 Статистика использования тегов:\n\n"

        if tag_usage:
            sorted_usage = sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)

            for tag_name, count in sorted_usage:
                if count > 0:
                    response += f"🏷️ {tag_name}: {count} раз\n"
                else:
                    response += f"🏷️ {tag_name}: не использовался\n"
        else:
            response += "У вас пока нет статистики по тегам."

        await callback.message.edit_text(
            response,
            reply_markup=get_back_keyboard("tags_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при получении статистики тегов: {e}")

@router.callback_query(F.data == "tags_menu")
async def callback_tags_menu(callback: CallbackQuery):
    """Обработчик возврата в меню тегов"""
    try:
        await callback.message.edit_text(
            "🏷️ Управление тегами\n\nВыберите действие:",
            reply_markup=get_back_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при возврате в меню тегов: {e}")

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
