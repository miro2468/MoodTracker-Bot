from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Главная reply клавиатура"""
    builder = ReplyKeyboardBuilder()

    builder.button(text="📊 Записать настроение")
    builder.button(text="📝 Дневник")
    builder.button(text="🏷️ Мои теги")
    builder.button(text="📈 Аналитика")
    builder.button(text="⚙️ Настройки")
    builder.button(text="ℹ️ Помощь")

    builder.adjust(3, 3)
    return builder.as_markup(resize_keyboard=True)

def get_mood_quick_reply() -> ReplyKeyboardMarkup:
    """Быстрая клавиатура для оценки настроения"""
    builder = ReplyKeyboardBuilder()

    builder.button(text="😢 Очень плохо")
    builder.button(text="😕 Плохо")
    builder.button(text="😐 Нейтрально")
    builder.button(text="🙂 Хорошо")
    builder.button(text="😊 Отлично")

    builder.adjust(5)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены"""
    builder = ReplyKeyboardBuilder()

    builder.button(text="❌ Отмена")

    return builder.as_markup(resize_keyboard=True)
