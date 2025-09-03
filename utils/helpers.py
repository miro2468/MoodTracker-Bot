import re
from datetime import datetime, date, timedelta
from typing import Optional, Tuple
from config import config

def format_mood_entry(entry, tags: list = None) -> str:
    """Форматировать запись настроения для отображения"""
    emoji = config.MOOD_EMOJIS[entry.mood_score]
    mood_name = config.MOOD_NAMES[entry.mood_score]

    message = f"🌟 Запись настроения за {entry.entry_date}\n\n"
    message += f"😊 Настроение: {emoji} {entry.mood_score}/5 ({mood_name})\n"

    if tags:
        tag_names = [tag.name for tag in tags]
        message += f"🏷️ Теги: {', '.join(tag_names)}\n"

    if entry.diary_text:
        message += f"\n📝 Заметка:\n{entry.diary_text}\n"

    message += f"\n✅ Запись сохранена в {entry.created_at.strftime('%H:%M')}"

    return message

def validate_diary_text(text: str) -> Tuple[bool, str]:
    """Валидация текста дневника"""
    if len(text) > config.DIARY_TEXT_LIMIT:
        return False, f"Текст слишком длинный. Максимум {config.DIARY_TEXT_LIMIT} символов."

    if not text.strip():
        return False, "Текст не может быть пустым."

    return True, "OK"

def parse_time_string(time_str: str) -> Optional[datetime.time]:
    """Парсинг строки времени в формате HH:MM"""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    if not re.match(pattern, time_str):
        return None

    try:
        hours, minutes = map(int, time_str.split(':'))
        return datetime.time(hours, minutes)
    except ValueError:
        return None

def get_date_range(period: str) -> Tuple[date, date]:
    """Получить диапазон дат для периода"""
    today = date.today()

    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    elif period == "quarter":
        start_date = today - timedelta(days=90)
    elif period == "year":
        start_date = today - timedelta(days=365)
    else:
        # По умолчанию неделя
        start_date = today - timedelta(days=7)

    return start_date, today

def format_stats_message(stats) -> str:
    """Форматировать сообщение со статистикой"""
    message = f"📊 Статистика за {stats.period}\n\n"
    message += f"📈 Среднее настроение: {stats.average_mood}/5\n"
    message += f"🎯 Дней с записями: {stats.total_entries}\n"

    if stats.best_day:
        message += f"📅 Лучший день: {stats.best_day}\n"

    if stats.worst_day:
        message += f"📉 Худший день: {stats.worst_day}\n"

    if stats.most_frequent_tags:
        message += "\n🏆 Самые частые теги:\n"
        for i, (tag_name, count) in enumerate(stats.most_frequent_tags[:5], 1):
            message += f"{i}. {tag_name} ({count} раз{'а' if count % 10 == 1 and count != 11 else 'раз'})\n"

    return message

def get_mood_color(score: int) -> str:
    """Получить цвет для оценки настроения"""
    if score >= 5:
        return config.CHART_COLORS['excellent']
    elif score >= 4:
        return config.CHART_COLORS['good']
    elif score >= 3:
        return config.CHART_COLORS['neutral']
    elif score >= 2:
        return config.CHART_COLORS['bad']
    else:
        return config.CHART_COLORS['terrible']

def format_patterns_message(patterns: list) -> str:
    """Форматировать сообщение с паттернами настроения"""
    if not patterns:
        return "🔍 Паттерны не найдены. Нужно больше записей для анализа."

    message = "🔍 Анализ паттернов настроения\n\n"

    # Сортируем по абсолютному значению корреляции
    patterns.sort(key=lambda x: abs(x.correlation), reverse=True)

    for pattern in patterns[:10]:  # Показываем топ 10
        trend = "📈" if pattern.correlation > 0 else "📉"
        correlation_text = f"+{pattern.correlation}" if pattern.correlation > 0 else str(pattern.correlation)

        message += f"{trend} {pattern.tag_name}\n"
        message += f"   Корреляция: {correlation_text}\n"
        message += f"   Положительных записей: {pattern.positive_entries}/{pattern.total_entries}\n\n"

    return message

def escape_markdown(text: str) -> str:
    """Экранирование специальных символов Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезать текст до максимальной длины"""
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."

def get_weekday_name(date_obj: date) -> str:
    """Получить название дня недели на русском"""
    weekdays = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }
    return weekdays[date_obj.weekday()]
