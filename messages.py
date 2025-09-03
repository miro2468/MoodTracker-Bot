"""
Файл с текстовыми сообщениями для MoodTracker Bot
Централизованное управление всеми текстовыми сообщениями для лучшего UX
"""

from config import config

class Messages:
    """Класс с текстовыми сообщениями бота"""

    # Приветственные сообщения
    WELCOME_MESSAGE = """
🌟 <b>Добро пожаловать в MoodTracker Bot!</b>

Ваш персональный помощник для отслеживания эмоционального благополучия.

🎯 <b>Что умеет бот:</b>
• 📊 Отслеживание настроения каждый день
• 🏷️ Анализ факторов влияния с помощью тегов
• 📝 Ведение дневника эмоций
• 📈 Красивые графики и аналитика
• ⏰ Умные напоминания

💡 <b>Как начать:</b>
Используйте кнопки меню ниже или отправьте /start
"""

    # Сообщения об ошибках
    ERROR_DB_CONNECTION = "❌ Ошибка подключения к базе данных"
    ERROR_INVALID_INPUT = "❌ Неверный формат данных. Попробуйте еще раз"
    ERROR_PERMISSION_DENIED = "❌ Недостаточно прав для выполнения действия"
    ERROR_UNKNOWN_COMMAND = "❌ Неизвестная команда. Используйте /help для справки"
    ERROR_SERVICE_UNAVAILABLE = "❌ Сервис временно недоступен. Попробуйте позже"

    # Сообщения об успехе
    SUCCESS_MOOD_SAVED = "✅ Настроение успешно сохранено!"
    SUCCESS_DIARY_SAVED = "✅ Запись в дневник добавлена!"
    SUCCESS_TAG_CREATED = "✅ Тег успешно создан!"
    SUCCESS_SETTINGS_UPDATED = "✅ Настройки обновлены!"
    SUCCESS_DATA_EXPORTED = "✅ Данные успешно экспортированы!"

    # Сообщения меню
    MENU_MAIN = "🏠 <b>Главное меню</b>\n\nВыберите действие:"
    MENU_MOOD = "🌟 <b>Запись настроения</b>\n\nКакое у вас настроение сегодня?"
    MENU_DIARY = "📝 <b>Дневник эмоций</b>\n\nУправление записями:"
    MENU_TAGS = "🏷️ <b>Управление тегами</b>\n\nВаши теги:"
    MENU_ANALYTICS = "📈 <b>Аналитика настроения</b>\n\nВыберите тип анализа:"
    MENU_SETTINGS = "⚙️ <b>Настройки</b>\n\nПерсональные настройки:"

    # Сообщения о тегах
    TAGS_EMPTY = "🏷️ У вас пока нет тегов.\n\nСоздайте первый тег для более точного анализа настроения!"
    TAGS_SELECTED = "🏷️ Выбрано тегов: {count}"
    TAGS_CATEGORY_SELECT = "🏷️ Выберите категорию тегов:"
    TAGS_IN_CATEGORY = "🏷️ Теги в категории <b>{category}</b>:"

    # Сообщения о статистике
    STATS_NO_DATA = "📊 У вас пока нет данных для анализа.\n\nНачните с создания записей настроения!"
    STATS_PERIOD = "📊 Статистика за период <b>{period}</b>"
    STATS_AVERAGE = "📈 Среднее настроение: <b>{avg:.1f}/5</b>"
    STATS_TOTAL_ENTRIES = "🎯 Всего записей: <b>{count}</b>"
    STATS_BEST_DAY = "📅 Лучший день: <b>{day}</b> ({mood:.1f}/5)"
    STATS_WORST_DAY = "📉 Худший день: <b>{day}</b> ({mood:.1f}/5)"

    # Сообщения о дневнике
    DIARY_EMPTY = "📝 Ваш дневник пуст.\n\nНачните с первой записи!"
    DIARY_ENTRIES_COUNT = "📝 Записей в дневнике: <b>{count}</b>"
    DIARY_RECENT_ENTRIES = "📖 <b>Последние записи:</b>"
    DIARY_ENTRY_FORMAT = """
📌 <b>{date}</b> {time}
{mood_emoji} Настроение: <b>{mood_name}</b> ({score}/5)
🏷️ Теги: {tags}
📝 {text}
"""

    # Сообщения о напоминаниях
    REMINDER_ENABLED = "⏰ Напоминания <b>включены</b> на {time}"
    REMINDER_DISABLED = "⏰ Напоминания <b>отключены</b>"
    REMINDER_TIME_SET = "⏰ Время напоминаний установлено на <b>{time}</b>"
    REMINDER_MOTIVATIONAL = [
        "🌟 Не забудьте записать свое настроение сегодня!",
        "📊 Ваш дневник эмоций ждет новых записей!",
        "💭 Как прошел ваш день? Расскажите об этом!",
        "🌈 Каждый день уникален - отметьте его настроение!",
        "📝 Ведение дневника поможет лучше понимать себя!",
    ]

    # Сообщения о графиках
    CHART_GENERATED = "📊 График успешно создан!"
    CHART_NO_DATA = "📊 Недостаточно данных для построения графика"
    CHART_TREND_TITLE = "📈 Тренд настроения за {period}"
    CHART_WEEKDAY_TITLE = "📅 Настроение по дням недели"
    CHART_TAGS_TITLE = "🏷️ Распределение тегов"

    # Сообщения о экспорте
    EXPORT_START = "📤 Начинаем экспорт данных..."
    EXPORT_SUCCESS = "✅ Экспорт завершен!\n\n📊 Всего записей: <b>{count}</b>"
    EXPORT_FORMAT = "📄 Формат: <b>{format}</b>"
    EXPORT_FILE_READY = "📎 Файл готов к скачиванию"

    # Справка
    HELP_COMMAND = """
📋 <b>Справка по командам:</b>

/start - Начать работу с ботом
/mood - Быстрая запись настроения
/diary - Открыть дневник эмоций
/stats - Показать статистику
/tags - Управление тегами
/settings - Настройки бота
/help - Показать эту справку

💡 <b>Полезные советы:</b>
• Записывайте настроение регулярно для лучших результатов
• Используйте теги для анализа факторов влияния
• Ведите дневник для более глубокого понимания эмоций
"""

    # Сообщения об обновлениях
    UPDATE_AVAILABLE = "🔄 Доступно обновление бота!"
    UPDATE_INSTALLED = "✅ Обновление установлено успешно!"

    @staticmethod
    def format_mood_entry(entry, tags_list=None):
        """Форматировать запись настроения для красивого отображения"""
        if tags_list is None:
            tags_list = []

        emoji = config.MOOD_EMOJIS.get(entry.mood_score, "😐")
        mood_name = config.MOOD_NAMES.get(entry.mood_score, "Неизвестно")

        # Форматируем время
        time_str = ""
        if entry.created_at:
            time_str = f" в {entry.created_at.strftime('%H:%M')}"

        # Форматируем теги
        tags_str = ""
        if tags_list:
            tag_names = [tag.name for tag in tags_list]
            tags_str = f"\n🏷️ Теги: {', '.join(tag_names)}"

        # Форматируем текст дневника
        diary_str = ""
        if entry.diary_text:
            diary_str = f"\n📝 Заметка: {entry.diary_text[:100]}"
            if len(entry.diary_text) > 100:
                diary_str += "..."

        return f"""🌟 Запись настроения за {entry.entry_date}

{emoji} Настроение: <b>{mood_name}</b> ({entry.mood_score}/5){tags_str}{diary_str}

✅ Запись сохранена{time_str}"""

    @staticmethod
    def format_stats_message(stats):
        """Форматировать сообщение со статистикой"""
        message = f"{Messages.STATS_PERIOD.format(period=stats.period)}\n\n"
        message += f"{Messages.STATS_AVERAGE.format(avg=stats.average_mood)}\n"
        message += f"{Messages.STATS_TOTAL_ENTRIES.format(count=stats.total_entries)}\n"

        if stats.best_day:
            message += f"{Messages.STATS_BEST_DAY.format(day=stats.best_day, mood=0)}\n"

        if stats.worst_day:
            message += f"{Messages.STATS_WORST_DAY.format(day=stats.worst_day, mood=0)}\n"

        if stats.most_frequent_tags:
            message += "\n🏆 <b>Самые частые теги:</b>\n"
            for i, (tag_name, count) in enumerate(stats.most_frequent_tags[:5], 1):
                message += f"{i}. {tag_name} ({count} раз{'а' if count % 10 == 1 and count != 11 else 'раз'})\n"

        return message

    @staticmethod
    def get_motivational_message():
        """Получить случайное мотивационное сообщение"""
        import random
        return random.choice(Messages.REMINDER_MOTIVATIONAL)

    @staticmethod
    def format_error_message(error_type, details=None):
        """Форматировать сообщение об ошибке"""
        base_messages = {
            'db_error': Messages.ERROR_DB_CONNECTION,
            'invalid_input': Messages.ERROR_INVALID_INPUT,
            'permission_denied': Messages.ERROR_PERMISSION_DENIED,
            'unknown_command': Messages.ERROR_UNKNOWN_COMMAND,
            'service_unavailable': Messages.ERROR_SERVICE_UNAVAILABLE,
        }

        message = base_messages.get(error_type, Messages.ERROR_UNKNOWN_COMMAND)

        if details:
            message += f"\n\n📋 <i>Детали: {details}</i>"

        return message

# Глобальный экземпляр сообщений
messages = Messages()
