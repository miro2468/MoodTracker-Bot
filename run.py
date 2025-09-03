#!/usr/bin/env python3
"""
Запуск MoodTracker Bot

Этот файл проверяет все зависимости и корректно запускает бота.
Используйте этот файл вместо прямого запуска bot.py для лучшей обработки ошибок.
"""

import sys
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    return True

def check_dependencies():
    """Проверка наличия зависимостей"""
    required_modules = [
        'aiogram',
        'matplotlib',
        'pandas',
        'seaborn',
        'PIL',
        'apscheduler',
        'dotenv'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("❌ Отсутствуют необходимые модули:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nУстановите зависимости:")
        print("  pip install -r requirements.txt")
        return False

    return True

def check_env_file():
    """Проверка наличия файла .env"""
    if not Path('.env').exists():
        print("⚠️  Файл .env не найден!")
        print("Создайте файл .env на основе .env.example и добавьте BOT_TOKEN")
        print("\nПример:")
        print("  BOT_TOKEN=ваш_токен_бота")
        print("\nПолучить токен можно у @BotFather в Telegram")
        return False
    return True

def check_env_variables():
    """Проверка переменных окружения"""
    from dotenv import load_dotenv
    load_dotenv()

    bot_token = os.getenv('BOT_TOKEN')

    if not bot_token:
        print("❌ BOT_TOKEN не найден в файле .env")
        print("Добавьте BOT_TOKEN=ваш_токен_бота в файл .env")
        return False

    if not bot_token.startswith(('123456789:', '987654321:')) or len(bot_token) < 45:
        print("⚠️  BOT_TOKEN выглядит подозрительно")
        print("Убедитесь, что токен получен от @BotFather")
        print("Пример корректного токена: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789")

    return True

def create_directories():
    """Создание необходимых директорий"""
    directories = ['database', 'handlers', 'keyboards', 'utils']

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Главная функция запуска"""
    print("🚀 Запуск MoodTracker Bot...")
    print("=" * 50)

    # Проверки
    checks = [
        ("Версия Python", check_python_version),
        ("Зависимости", check_dependencies),
        ("Файл .env", check_env_file),
        ("Переменные окружения", check_env_variables)
    ]

    all_passed = True

    for check_name, check_func in checks:
        print(f"Проверка: {check_name}...")
        if check_func():
            print(f"✅ {check_name}: OK")
        else:
            print(f"❌ {check_name}: FAILED")
            all_passed = False

    if not all_passed:
        print("\n❌ Некоторые проверки не пройдены.")
        print("Исправьте проблемы и попробуйте снова.")
        sys.exit(1)

    # Создание директорий
    print("\nСоздание директорий...")
    create_directories()
    print("✅ Директории созданы")

    # Запуск бота
    print("\n🚀 Запуск бота...")
    print("=" * 50)

    try:
        # Импорт и запуск основного модуля
        import bot
        import asyncio

        # Запуск асинхронной функции
        asyncio.run(bot.main())

    except KeyboardInterrupt:
        print("\n\n🛑 Бот остановлен пользователем")
        print("Спасибо за использование MoodTracker Bot!")

    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}")
        print("Убедитесь, что все файлы проекта находятся в правильных местах")

    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        logger.exception("Критическая ошибка при запуске")
        print("\nПодробная информация записана в лог-файл")

if __name__ == "__main__":
    main()
