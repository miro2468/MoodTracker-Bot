from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.db_manager import db_manager
from keyboards.inline import (
    get_analytics_keyboard,
    get_back_keyboard,
    get_main_menu_keyboard
)
from keyboards.reply import get_main_reply_keyboard
from config import logger
from utils.charts import chart_generator
from utils.helpers import (
    get_date_range,
    format_stats_message,
    format_patterns_message
)
from aiogram.types import InputFile

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats - быстрая статистика"""
    try:
        user_id = message.from_user.id

        # Получаем статистику за последнюю неделю
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

        stats_message = format_stats_message(stats)
        await message.answer(stats_message)

    except Exception as e:
        logger.error(f"Ошибка в команде /stats для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при получении статистики.")

@router.message(F.text == "📈 Аналитика")
async def btn_analytics(message: Message):
    """Обработчик кнопки Аналитика"""
    await show_analytics_menu(message)

async def show_analytics_menu(message: Message):
    """Показать меню аналитики"""
    try:
        user_id = message.from_user.id

        # Проверяем, есть ли записи для анализа
        entries_count = len(db_manager.get_mood_entries(user_id, limit=1))

        if entries_count == 0:
            await message.answer(
                "📊 У вас пока нет данных для анализа.\n\n" +
                "Начните с создания первых записей настроения!",
                reply_markup=get_main_menu_keyboard()
            )
            return

        await message.answer(
            "📈 Аналитика настроения\n\nВыберите тип анализа:",
            reply_markup=get_analytics_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка при показе меню аналитики: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.callback_query(F.data.startswith("analytics_"))
async def callback_analytics_period(callback: CallbackQuery):
    """Обработчик выбора периода для аналитики"""
    try:
        period = callback.data.split("_")[1]
        user_id = callback.from_user.id

        # Определяем период
        if period == "week":
            start_date, end_date = get_date_range("week")
            period_name = "неделю"
        elif period == "month":
            start_date, end_date = get_date_range("month")
            period_name = "месяц"
        elif period == "quarter":
            start_date, end_date = get_date_range("quarter")
            period_name = "квартал"
        elif period == "year":
            start_date, end_date = get_date_range("year")
            period_name = "год"
        else:
            await callback.answer("❌ Неизвестный период")
            return

        # Получаем данные
        entries = db_manager.get_mood_entries(user_id, start_date, end_date)

        if not entries:
            await callback.message.edit_text(
                f"📊 За последний {period_name} записей не найдено.\n\n" +
                "Попробуйте выбрать другой период.",
                reply_markup=get_analytics_keyboard()
            )
            return

        # Генерируем график тренда
        chart_buffer = chart_generator.generate_mood_trend_chart(entries, start_date, end_date)

        # Получаем статистику
        stats = db_manager.get_mood_stats(user_id, start_date, end_date)
        stats_message = format_stats_message(stats)

        # Отправляем график
        try:
            await callback.message.delete()
        except Exception:
            pass  # Игнорируем ошибку если сообщение уже удалено

        # Создаем InputFile из BytesIO
        chart_file = InputFile(chart_buffer, filename=f"mood_chart_{period_name}.png")

        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=chart_file,
            caption=f"📈 График настроения за {period_name}\n\n{stats_message}",
            reply_markup=get_back_keyboard("analytics_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при генерации графика тренда: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при генерации графика.")

@router.callback_query(F.data == "analytics_days")
async def callback_analytics_days(callback: CallbackQuery):
    """Обработчик анализа по дням недели"""
    try:
        user_id = callback.from_user.id

        # Получаем все записи пользователя
        entries = db_manager.get_mood_entries(user_id)

        if len(entries) < 3:
            await callback.message.edit_text(
                "📅 Для анализа по дням недели нужно минимум 3 записи.\n\n" +
                "Продолжайте вести дневник настроения!",
                reply_markup=get_analytics_keyboard()
            )
            return

        # Генерируем график по дням недели
        chart_buffer = chart_generator.generate_weekday_stats_chart(entries)

        # Получаем статистику по дням
        weekday_stats = {}
        for entry in entries:
            weekday = entry.entry_date.weekday()
            if weekday not in weekday_stats:
                weekday_stats[weekday] = []
            weekday_stats[weekday].append(entry.mood_score)

        # Форматируем анализ
        weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        analysis_text = "📅 Анализ настроения по дням недели:\n\n"

        for weekday in range(7):
            if weekday in weekday_stats:
                scores = weekday_stats[weekday]
                avg_score = sum(scores) / len(scores)
                count = len(scores)

                day_name = weekday_names[weekday]
                emoji = "😊" if avg_score >= 4 else "😐" if avg_score >= 3 else "😢"

                analysis_text += f"{day_name}: {emoji} {avg_score:.1f}/5 ({count} записей)\n"
            else:
                analysis_text += f"{weekday_names[weekday]}: Нет данных\n"

        try:
            await callback.message.delete()
        except Exception:
            pass  # Игнорируем ошибку если сообщение уже удалено

        # Создаем InputFile из BytesIO
        chart_file = InputFile(chart_buffer, filename="weekday_stats.png")

        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=chart_file,
            caption=analysis_text,
            reply_markup=get_back_keyboard("analytics_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при анализе по дням недели: {e}")
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.callback_query(F.data == "analytics_tags")
async def callback_analytics_tags(callback: CallbackQuery):
    """Обработчик анализа по тегам"""
    try:
        user_id = callback.from_user.id

        # Получаем статистику по тегам
        # В реальном проекте нужно добавить метод для получения статистики тегов
        entries = db_manager.get_mood_entries(user_id)

        if not entries:
            await callback.message.edit_text(
                "🏷️ Нет данных для анализа тегов.",
                reply_markup=get_analytics_keyboard()
            )
            return

        # Собираем статистику по тегам
        tag_stats = {}
        total_entries = len(entries)

        # Получаем все теги пользователя
        all_tags = db_manager.get_all_tags(user_id)

        for tag in all_tags:
            # Считаем, сколько раз тег использовался
            tag_usage = 0
            for entry in entries:
                # В реальном проекте нужно получить связи entry-tag из базы
                # Пока что это заглушка
                pass

            if tag_usage > 0:
                tag_stats[tag.name] = tag_usage

        if not tag_stats:
            await callback.message.edit_text(
                "🏷️ У вас пока нет тегов для анализа.\n\n" +
                "Добавляйте теги при записи настроения для более глубокого анализа!",
                reply_markup=get_analytics_keyboard()
            )
            return

        # Генерируем круговую диаграмму
        chart_buffer = chart_generator.generate_tags_pie_chart(tag_stats)

        # Форматируем текст анализа
        analysis_text = "🏷️ Анализ использования тегов:\n\n"

        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)
        for tag_name, count in sorted_tags[:10]:  # Топ 10 тегов
            percentage = (count / total_entries) * 100 if total_entries > 0 else 0
            analysis_text += f"#{tag_name}: {count} раз ({percentage:.1f}%)\n"

        try:
            await callback.message.delete()
        except Exception:
            pass  # Игнорируем ошибку если сообщение уже удалено

        # Создаем InputFile из BytesIO
        chart_file = InputFile(chart_buffer, filename="tags_pie_chart.png")

        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=chart_file,
            caption=analysis_text,
            reply_markup=get_back_keyboard("analytics_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при анализе по тегам: {e}")
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.callback_query(F.data == "analytics_patterns")
async def callback_analytics_patterns(callback: CallbackQuery):
    """Обработчик поиска паттернов настроения"""
    try:
        user_id = callback.from_user.id

        # Получаем паттерны
        patterns = db_manager.get_mood_patterns(user_id)

        if not patterns:
            await callback.message.edit_text(
                "🔍 Паттерны не найдены.\n\n" +
                "Для поиска паттернов нужно больше записей с тегами (минимум 5 записей на тег).",
                reply_markup=get_analytics_keyboard()
            )
            return

        # Генерируем распределение настроения
        entries = db_manager.get_mood_entries(user_id)
        chart_buffer = chart_generator.generate_mood_distribution_chart(entries)

        # Форматируем паттерны
        patterns_message = format_patterns_message(patterns)

        try:
            await callback.message.delete()
        except Exception:
            pass  # Игнорируем ошибку если сообщение уже удалено

        # Создаем InputFile из BytesIO
        chart_file = InputFile(chart_buffer, filename="mood_patterns.png")

        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=chart_file,
            caption=patterns_message,
            reply_markup=get_back_keyboard("analytics_menu")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при поиске паттернов: {e}")
        await callback.message.edit_text("❌ Произошла ошибка.")

@router.callback_query(F.data == "analytics_menu")
async def callback_analytics_menu(callback: CallbackQuery):
    """Обработчик возврата в меню аналитики"""
    try:
        await callback.message.edit_text(
            "📈 Аналитика настроения\n\nВыберите тип анализа:",
            reply_markup=get_analytics_keyboard()
        )
        await callback.answer()
    except Exception as e:
        # Если сообщение нельзя отредактировать, отправляем новое
        logger.warning(f"Не удалось отредактировать сообщение, отправляем новое: {e}")
        try:
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="📈 Аналитика настроения\n\nВыберите тип анализа:",
                reply_markup=get_analytics_keyboard()
            )
        except Exception as e2:
            logger.error(f"Не удалось отправить новое сообщение: {e2}")
        await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    """Обработчик возврата в главное меню"""
    try:
        await callback.message.edit_text(
            "🏠 Выберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при возврате в главное меню: {e}")
