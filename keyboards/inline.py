from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура меню"""
    builder = InlineKeyboardBuilder()

    builder.button(text="📊 Записать настроение", callback_data="mood_record")
    builder.button(text="📝 Дневник", callback_data="diary_menu")
    builder.button(text="🏷️ Мои теги", callback_data="tags_menu")
    builder.button(text="📈 Аналитика", callback_data="analytics_menu")
    builder.button(text="⚙️ Настройки", callback_data="settings_menu")

    builder.adjust(2, 2, 1)
    return builder.as_markup()

def get_mood_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оценки настроения"""
    builder = InlineKeyboardBuilder()

    for score in range(1, 6):
        emoji = config.MOOD_EMOJIS[score]
        name = config.MOOD_NAMES[score]
        builder.button(
            text=f"{emoji} {score} - {name}",
            callback_data=f"mood_select_{score}"
        )

    builder.adjust(1)
    return builder.as_markup()

def get_tags_selection_keyboard(tags: list, selected_tags: list = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора тегов"""
    if selected_tags is None:
        selected_tags = []

    builder = InlineKeyboardBuilder()

    # Группируем теги по категориям
    categories = {}
    for tag in tags:
        category = tag.category or "Другие"
        if category not in categories:
            categories[category] = []
        categories[category].append(tag)

    # Создаем кнопки по категориям
    for category, category_tags in categories.items():
        # Добавляем заголовок категории
        builder.button(
            text=f"📂 {category}",
            callback_data=f"category_{category.lower().replace(' ', '_')}"
        )

        # Добавляем теги категории
        for tag in category_tags:
            is_selected = tag.id in selected_tags
            status = "✅" if is_selected else "☐"
            builder.button(
                text=f"{status} {tag.name}",
                callback_data=f"tag_toggle_{tag.id}"
            )

    # Кнопки управления
    builder.button(text="➕ Создать тег", callback_data="tag_create")
    builder.button(text="✅ Готово", callback_data="tags_done")
    builder.button(text="🔄 Сбросить", callback_data="tags_reset")

    builder.adjust(1)
    return builder.as_markup()

def get_diary_actions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура действий с дневником"""
    builder = InlineKeyboardBuilder()

    builder.button(text="📝 Написать запись", callback_data="diary_write")
    builder.button(text="📖 Просмотреть записи", callback_data="diary_view")
    builder.button(text="🔍 Поиск по записям", callback_data="diary_search")
    builder.button(text="📅 Записи за период", callback_data="diary_period")

    builder.adjust(2, 2)
    return builder.as_markup()

def get_analytics_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура аналитики"""
    builder = InlineKeyboardBuilder()

    builder.button(text="📊 График за неделю", callback_data="analytics_week")
    builder.button(text="📈 График за месяц", callback_data="analytics_month")
    builder.button(text="📅 График за квартал", callback_data="analytics_quarter")
    builder.button(text="📊 График за год", callback_data="analytics_year")
    builder.button(text="📅 Статистика по дням", callback_data="analytics_days")
    builder.button(text="🏷️ Анализ тегов", callback_data="analytics_tags")
    builder.button(text="🔍 Поиск паттернов", callback_data="analytics_patterns")

    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    builder = InlineKeyboardBuilder()

    builder.button(text="⏰ Время напоминания", callback_data="settings_reminder_time")
    builder.button(text="🔔 Напоминания", callback_data="settings_reminders")
    builder.button(text="🌍 Часовой пояс", callback_data="settings_timezone")
    builder.button(text="📤 Экспорт данных", callback_data="settings_export")
    builder.button(text="🔄 Сброс данных", callback_data="settings_reset")

    builder.adjust(2, 2, 1)
    return builder.as_markup()

def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Да", callback_data=f"confirm_{action}")
    builder.button(text="❌ Нет", callback_data=f"cancel_{action}")

    builder.adjust(2)
    return builder.as_markup()

def get_back_keyboard(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()

    builder.button(text="⬅️ Назад", callback_data=callback_data)

    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отмены"""
    builder = InlineKeyboardBuilder()

    builder.button(text="❌ Отмена", callback_data="cancel")

    return builder.as_markup()
