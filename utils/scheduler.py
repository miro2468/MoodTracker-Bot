import logging
from datetime import datetime, time
from typing import Dict, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.db_manager import db_manager
from config import config

logger = logging.getLogger(__name__)

class ReminderScheduler:
    """Планировщик напоминаний о записи настроения"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.active_jobs: Dict[int, str] = {}  # user_id -> job_id

    async def start_scheduler(self):
        """Запуск планировщика"""
        self.scheduler.start()
        logger.info("Планировщик напоминаний запущен")

        # Загрузка активных напоминаний из базы данных
        await self.load_active_reminders()

    async def stop_scheduler(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик напоминаний остановлен")

    async def load_active_reminders(self):
        """Загрузка активных напоминаний"""
        # Получаем всех пользователей с активными напоминаниями
        # В реальном проекте нужно добавить поле для хранения job_id в базе данных
        # Пока что это заглушка
        pass

    async def schedule_user_reminder(self, user_id: int, reminder_time: time):
        """Установка напоминания для пользователя"""
        # Отменяем предыдущее напоминание, если оно было
        await self.cancel_user_reminder(user_id)

        # Создаем новое напоминание
        job_id = f"reminder_{user_id}"

        self.scheduler.add_job(
            func=self.send_reminder,
            trigger=CronTrigger(hour=reminder_time.hour, minute=reminder_time.minute),
            id=job_id,
            args=[user_id],
            name=f"Daily reminder for user {user_id}"
        )

        self.active_jobs[user_id] = job_id
        logger.info(f"Установлено напоминание для пользователя {user_id} на {reminder_time}")

    async def cancel_user_reminder(self, user_id: int):
        """Отмена напоминания для пользователя"""
        if user_id in self.active_jobs:
            job_id = self.active_jobs[user_id]
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            del self.active_jobs[user_id]
            logger.info(f"Отменено напоминание для пользователя {user_id}")

    async def send_reminder(self, user_id: int):
        """Отправка напоминания пользователю"""
        # Получаем настройки пользователя
        settings = db_manager.get_user_settings(user_id)

        if not settings.daily_reminder:
            return

        # Проверяем, была ли уже запись сегодня
        today_entry = db_manager.get_today_mood(user_id)

        if today_entry:
            # Пользователь уже записал настроение сегодня
            return

        # Здесь должна быть логика отправки сообщения пользователю
        # В реальном проекте нужно передать bot экземпляр или использовать callback
        logger.info(f"Отправлено напоминание пользователю {user_id}")

    async def send_adaptive_reminder(self, user_id: int):
        """Отправка адаптивного напоминания (если пользователь давно не записывал)"""
        # Получаем последнюю запись пользователя
        entries = db_manager.get_mood_entries(user_id, limit=1)

        if not entries:
            # Пользователь никогда не записывал настроение
            logger.info(f"Отправлено первое напоминание пользователю {user_id}")
            return

        last_entry = entries[0]
        days_since_last_entry = (datetime.now().date() - last_entry.entry_date).days

        if days_since_last_entry > 3:
            # Пользователь не записывал больше 3 дней
            logger.info(f"Отправлено адаптивное напоминание пользователю {user_id} "
                       f"(последняя запись {days_since_last_entry} дней назад)")

    async def update_all_reminders(self):
        """Обновление всех активных напоминаний"""
        # В реальном проекте здесь нужно получить всех пользователей из базы данных
        # и обновить их напоминания согласно настройкам
        pass

    def get_active_reminders_count(self) -> int:
        """Получить количество активных напоминаний"""
        return len(self.active_jobs)

    def get_user_reminder_info(self, user_id: int) -> Dict:
        """Получить информацию о напоминании пользователя"""
        if user_id not in self.active_jobs:
            return {"active": False}

        job_id = self.active_jobs[user_id]
        job = self.scheduler.get_job(job_id)

        if job:
            next_run = job.next_run_time
            return {
                "active": True,
                "next_run": next_run.isoformat() if next_run else None,
                "job_id": job_id
            }

        return {"active": False}

# Глобальный экземпляр планировщика
reminder_scheduler = ReminderScheduler()
