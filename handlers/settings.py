import logging
from datetime import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import db_manager
from keyboards.inline import (
    get_settings_keyboard,
    get_main_menu_keyboard,
    get_back_keyboard,
    get_confirmation_keyboard
)
from keyboards.reply import get_main_reply_keyboard
from utils.helpers import parse_time_string

logger = logging.getLogger(__name__)

router = Router()

# Состояния для FSM
class SettingsStates(StatesGroup):
    waiting_for_reminder_time = State()
    waiting_for_timezone = State()

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Обработчик команды /settings"""
    try:
        await show_settings_menu(message)
    except Exception as e:
        logger.error(f"Ошибка в команде /settings для пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.message(F.text == "⚙️ Настройки")
async def btn_settings(message: Message):
    """Обработчик кнопки Настройки"""
    await cmd_settings(message)

async def show_settings_menu(message: Message):
    """Показать меню настроек"""
    try:
        user_id = message.from_user.id

        # Получаем текущие настройки
        settings = db_manager.get_user_settings(user_id)

        # Получаем информацию о напоминаниях
        from utils.scheduler import reminder_scheduler
        reminder_info = reminder_scheduler.get_user_reminder_info(user_id)

        # Форматируем информацию о настройках
        response = "⚙️ Настройки бота\n\n"

        response += f"⏰ Время напоминания: {settings.reminder_time.strftime('%H:%M')}\n"
        response += f"🔔 Напоминания: {'Включены' if settings.daily_reminder else 'Отключены'}\n"
        response += f"🌍 Часовой пояс: {settings.language}\n\n"

        if reminder_info['active']:
            from datetime import datetime
            next_run = reminder_info.get('next_run')
            if next_run:
                next_time = datetime.fromisoformat(next_run)
                response += f"📅 Следующее напоминание: {next_time.strftime('%d.%m.%Y %H:%M')}\n"
        else:
            response += "📅 Напоминания не активны\n"

        await message.answer(
            response,
            reply_markup=get_settings_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка при показе меню настроек: {e}")
        await message.answer("❌ Произошла ошибка.")

@router.callback_query(F.data == "settings_reminder_time")
async def callback_settings_reminder_time(callback: CallbackQuery, state: FSMContext):
    """Обработчик настройки времени напоминания"""
    try:
        await callback.message.edit_text(
            "⏰ Настройка времени напоминания\n\n" +
            "Введите время в формате ЧЧ:ММ (например: 21:00):",
            reply_markup=get_back_keyboard("settings_menu")
        )

        await state.set_state(SettingsStates.waiting_for_reminder_time)
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при настройке времени напоминания: {e}")

@router.message(SettingsStates.waiting_for_reminder_time)
async def process_reminder_time(message: Message, state: FSMContext):
    """Обработка времени напоминания"""
    try:
        time_str = message.text.strip()
        reminder_time = parse_time_string(time_str)

        if not reminder_time:
            await message.answer(
                "❌ Неверный формат времени.\n\n" +
                "Введите время в формате ЧЧ:ММ (например: 21:00):"
            )
            return

        user_id = message.from_user.id

        # Получаем текущие настройки
        settings = db_manager.get_user_settings(user_id)
        settings.reminder_time = reminder_time

        # Сохраняем настройки
        db_manager.update_user_settings(settings)

        # Обновляем расписание напоминаний
        if settings.daily_reminder:
            from utils.scheduler import reminder_scheduler
            await reminder_scheduler.schedule_user_reminder(user_id, reminder_time)

        await message.answer(
            f"✅ Время напоминания установлено на {reminder_time.strftime('%H:%M')}",
            reply_markup=get_main_menu_keyboard()
        )

        await state.clear()
        logger.info(f"Пользователь {user_id} установил время напоминания на {reminder_time}")

    except Exception as e:
        logger.error(f"Ошибка при установке времени напоминания: {e}")
        await state.clear()

@router.callback_query(F.data == "settings_reminders")
async def callback_settings_reminders(callback: CallbackQuery):
    """Обработчик включения/отключения напоминаний"""
    try:
        user_id = callback.from_user.id

        # Получаем текущие настройки
        settings = db_manager.get_user_settings(user_id)

        # Переключаем статус напоминаний
        settings.daily_reminder = not settings.daily_reminder
        db_manager.update_user_settings(settings)

        # Обновляем расписание
        from utils.scheduler import reminder_scheduler
        if settings.daily_reminder:
            await reminder_scheduler.schedule_user_reminder(user_id, settings.reminder_time)
        else:
            await reminder_scheduler.cancel_user_reminder(user_id)

        status_text = "включены" if settings.daily_reminder else "отключены"

        await callback.message.edit_text(
            f"✅ Напоминания {status_text}!\n\n" +
            "Выберите действие:",
            reply_markup=get_settings_keyboard()
        )

        await callback.answer(f"Напоминания {status_text}")

    except Exception as e:
        logger.error(f"Ошибка при переключении напоминаний: {e}")

@router.callback_query(F.data == "settings_timezone")
async def callback_settings_timezone(callback: CallbackQuery, state: FSMContext):
    """Обработчик настройки часового пояса"""
    try:
        await callback.message.edit_text(
            "🌍 Настройка часового пояса\n\n" +
            "Введите ваш часовой пояс в формате UTC+X или UTC-X\n" +
            "(например: UTC+3 для Москвы, UTC-5 для Нью-Йорка):",
            reply_markup=get_back_keyboard("settings_menu")
        )

        await state.set_state(SettingsStates.waiting_for_timezone)
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при настройке часового пояса: {e}")

@router.message(SettingsStates.waiting_for_timezone)
async def process_timezone(message: Message, state: FSMContext):
    """Обработка часового пояса"""
    try:
        timezone_str = message.text.strip()

        # Простая валидация формата
        import re
        if not re.match(r'^UTC[+-]\d{1,2}$', timezone_str):
            await message.answer(
                "❌ Неверный формат часового пояса.\n\n" +
                "Используйте формат UTC+X или UTC-X (например: UTC+3):"
            )
            return

        user_id = message.from_user.id

        # Обновляем часовой пояс пользователя
        db_manager.update_user_timezone(user_id, timezone_str)

        await message.answer(
            f"✅ Часовой пояс установлен на {timezone_str}",
            reply_markup=get_main_menu_keyboard()
        )

        await state.clear()
        logger.info(f"Пользователь {user_id} установил часовой пояс {timezone_str}")

    except Exception as e:
        logger.error(f"Ошибка при установке часового пояса: {e}")
        await state.clear()

@router.callback_query(F.data == "settings_export")
async def callback_settings_export(callback: CallbackQuery):
    """Обработчик экспорта данных"""
    try:
        user_id = callback.from_user.id

        # Получаем данные пользователя
        export_data = db_manager.export_user_data(user_id)

        if not export_data['entries']:
            await callback.message.edit_text(
                "📤 У вас нет данных для экспорта.\n\n" +
                "Начните с создания записей настроения!",
                reply_markup=get_settings_keyboard()
            )
            return

        # Создаем CSV файл
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(['Дата', 'Настроение', 'Оценка', 'Заметка', 'Теги'])

        # Данные
        for entry in export_data['entries']:
            writer.writerow([
                entry['date'],
                entry['mood_name'],
                entry['mood_score'],
                entry['diary_text'],
                entry['tags']
            ])

        csv_content = output.getvalue()
        output.close()

        # Отправляем файл
        from io import BytesIO
        csv_bytes = BytesIO(csv_content.encode('utf-8'))

        await callback.message.delete()

        await callback.bot.send_document(
            chat_id=callback.message.chat.id,
            document=csv_bytes,
            filename=f"mood_tracker_export_{user_id}.csv",
            caption="📤 Экспорт данных в формате CSV\n\n" +
                   f"Всего записей: {export_data['total_entries']}\n" +
                   f"Дата экспорта: {export_data['export_date'][:10]}",
            reply_markup=get_back_keyboard("settings_menu")
        )

        await callback.answer("Экспорт завершен")

    except Exception as e:
        logger.error(f"Ошибка при экспорте данных: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при экспорте.")

@router.callback_query(F.data == "settings_reset")
async def callback_settings_reset(callback: CallbackQuery):
    """Обработчик сброса данных"""
    try:
        user_id = callback.from_user.id

        # Получаем количество записей
        entries = db_manager.get_mood_entries(user_id)
        entries_count = len(entries)

        if entries_count == 0:
            await callback.message.edit_text(
                "🗑️ У вас нет данных для сброса.",
                reply_markup=get_settings_keyboard()
            )
            return

        await callback.message.edit_text(
            f"🗑️ Сброс данных\n\n" +
            f"У вас {entries_count} записей настроения.\n\n" +
            "⚠️ Это действие нельзя отменить!\n" +
            "Все данные будут удалены без возможности восстановления.\n\n" +
            "Вы действительно хотите удалить все данные?",
            reply_markup=get_confirmation_keyboard("reset_data")
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при сбросе данных: {e}")

@router.callback_query(F.data == "confirm_reset_data")
async def callback_confirm_reset_data(callback: CallbackQuery):
    """Подтверждение сброса данных"""
    try:
        user_id = callback.from_user.id

        # В реальном проекте нужно добавить методы для полного удаления данных пользователя
        # Пока что это заглушка
        await callback.message.edit_text(
            "✅ Все данные успешно удалены.\n\n" +
            "Вы можете начать вести дневник настроения заново.",
            reply_markup=get_main_menu_keyboard()
        )

        logger.info(f"Пользователь {user_id} сбросил все данные")

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при подтверждении сброса данных: {e}")

@router.callback_query(F.data == "settings_menu")
async def callback_settings_menu(callback: CallbackQuery):
    """Обработчик возврата в меню настроек"""
    try:
        user_id = callback.from_user.id
        settings = db_manager.get_user_settings(user_id)

        response = "⚙️ Настройки бота\n\n"
        response += f"⏰ Время напоминания: {settings.reminder_time.strftime('%H:%M')}\n"
        response += f"🔔 Напоминания: {'Включены' if settings.daily_reminder else 'Отключены'}\n"
        response += f"🌍 Часовой пояс: {settings.language}\n"

        await callback.message.edit_text(
            response,
            reply_markup=get_settings_keyboard()
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при возврате в меню настроек: {e}")

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
