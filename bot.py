import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config, logger
from database.db_manager import db_manager
from utils.scheduler import reminder_scheduler

# Импорт хендлеров
from handlers.start import router as start_router
from handlers.mood import router as mood_router
from handlers.diary import router as diary_router
from handlers.analytics import router as analytics_router
from handlers.tags import router as tags_router
from handlers.settings import router as settings_router

async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("🚀 Начинаем инициализацию MoodTracker Bot...")

        # Проверяем токен бота
        if not config.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не найден в переменных окружения")
            print("❌ Ошибка: BOT_TOKEN не найден!")
            print("Создайте файл .env и добавьте BOT_TOKEN=ваш_токен_бота")
            print("Получить токен можно у @BotFather в Telegram")
            return

        logger.info("✅ BOT_TOKEN найден и загружен")

        # Инициализация бота
        logger.info("🤖 Инициализация Telegram бота...")
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        logger.info("✅ Бот инициализирован успешно")

        # Инициализация диспетчера
        logger.info("📋 Настройка диспетчера команд...")
        dp = Dispatcher()

        # Регистрация роутеров
        logger.info("🔗 Регистрация хендлеров...")
        dp.include_router(start_router)
        dp.include_router(mood_router)
        dp.include_router(diary_router)
        dp.include_router(analytics_router)
        dp.include_router(tags_router)
        dp.include_router(settings_router)
        logger.info("✅ Все хендлеры зарегистрированы")

        # Инициализация планировщика напоминаний
        logger.info("⏰ Запуск планировщика напоминаний...")
        await reminder_scheduler.start_scheduler()
        logger.info("✅ Планировщик напоминаний запущен")

        logger.info("🎉 MoodTracker Bot полностью запущен и готов к работе!")
        print("🚀 MoodTracker Bot запущен!")
        print("📊 Бот готов к работе")
        print("📝 Логи сохраняются в файл bot.log")
        print("Нажмите Ctrl+C для остановки")

        # Запуск бота
        logger.info("🔄 Запуск polling...")
        await dp.start_polling(bot)

    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем (Ctrl+C)")
        print("\n🛑 Бот остановлен")

    except Exception as e:
        logger.error(f"💥 Критическая ошибка при запуске бота: {e}", exc_info=True)
        print(f"❌ Критическая ошибка: {e}")
        print("Подробная информация записана в лог-файл")

    finally:
        # Остановка планировщика
        logger.info("🔄 Остановка планировщика напоминаний...")
        try:
            await reminder_scheduler.stop_scheduler()
            logger.info("✅ Планировщик остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке планировщика: {e}")

async def on_startup():
    """Действия при запуске бота"""
    try:
        logger.info("Выполнение действий при запуске...")

        # Инициализация базы данных
        # (базы данных инициализируется автоматически при импорте db_manager)

        logger.info("Действия при запуске выполнены успешно")

    except Exception as e:
        logger.error(f"Ошибка при выполнении действий при запуске: {e}")

async def on_shutdown():
    """Действия при остановке бота"""
    try:
        logger.info("Выполнение действий при остановке...")

        # Здесь можно добавить код для graceful shutdown
        # Например, сохранение состояния, закрытие соединений и т.д.

        logger.info("Действия при остановке выполнены успешно")

    except Exception as e:
        logger.error(f"Ошибка при выполнении действий при остановке: {e}")

if __name__ == "__main__":
    try:
        # Проверка зависимостей
        import sys
        required_modules = ['aiogram', 'matplotlib', 'pandas', 'seaborn']

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            print("❌ Отсутствуют необходимые модули:")
            for module in missing_modules:
                print(f"  - {module}")
            print("\nУстановите зависимости с помощью: pip install -r requirements.txt")
            sys.exit(1)

        # Запуск бота
        asyncio.run(main())

    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
