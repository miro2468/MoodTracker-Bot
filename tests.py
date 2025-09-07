"""
Простые тесты для MoodTracker Bot
==================================

Этот файл содержит базовые тесты для проверки основных функций бота.
Тесты написаны для начинающих разработчиков и легко понятны.

Запуск тестов:
python tests.py

Или с помощью pytest:
pytest tests.py
"""

import unittest
import sys
import os
from datetime import date, datetime
from unittest.mock import Mock, MagicMock

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем модули бота
from database.db_manager import DatabaseManager
from database.models import User, MoodEntry, Tag
from config import config
from utils.helpers import format_mood_entry
from keyboards.inline import get_main_menu_keyboard


class TestDatabaseManager(unittest.TestCase):
    """Тесты для менеджера базы данных"""

    def setUp(self):
        """Подготовка к тестам - создаем тестовую базу данных"""
        self.db = DatabaseManager()
        # Используем отдельную тестовую базу данных
        self.test_db_path = "test_mood_tracker.db"
        self.db = DatabaseManager(self.test_db_path)
        self.db.init_db()

        # Создаем тестового пользователя
        self.test_user = self.db.get_or_create_user(
            user_id=123456789,
            username="test_user",
            first_name="Test User"
        )

    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_create_user(self):
        """Тест создания нового пользователя"""
        print("🧪 Тестируем создание пользователя...")

        # Проверяем, что пользователь создан
        self.assertIsNotNone(self.test_user)
        self.assertEqual(self.test_user.user_id, 123456789)
        self.assertEqual(self.test_user.username, "test_user")
        self.assertEqual(self.test_user.first_name, "Test User")

        print("✅ Пользователь успешно создан!")

    def test_create_mood_entry(self):
        """Тест создания записи настроения"""
        print("🧪 Тестируем создание записи настроения...")

        # Создаем запись настроения
        mood_entry = self.db.create_mood_entry(
            user_id=self.test_user.user_id,
            mood_score=4,
            note="Тестовая запись настроения",
            tags=["работа", "спорт"]
        )

        # Проверяем запись
        self.assertIsNotNone(mood_entry)
        self.assertEqual(mood_entry.user_id, self.test_user.user_id)
        self.assertEqual(mood_entry.mood_score, 4)
        self.assertEqual(mood_entry.note, "Тестовая запись настроения")

        print("✅ Запись настроения успешно создана!")

    def test_get_mood_entries(self):
        """Тест получения записей настроения"""
        print("🧪 Тестируем получение записей настроения...")

        # Создаем несколько записей
        for i in range(3):
            self.db.create_mood_entry(
                user_id=self.test_user.user_id,
                mood_score=i + 1,
                note=f"Запись #{i+1}"
            )

        # Получаем записи
        entries = self.db.get_mood_entries(self.test_user.user_id)

        # Проверяем результат
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].mood_score, 3)  # Самая свежая запись
        self.assertEqual(entries[-1].mood_score, 1)  # Самая старая запись

        print("✅ Записи настроения успешно получены!")

    def test_get_mood_stats(self):
        """Тест получения статистики настроения"""
        print("🧪 Тестируем получение статистики настроения...")

        # Создаем тестовые записи
        test_date = date.today()
        for score in [1, 3, 5, 4, 2, 5, 3]:
            self.db.create_mood_entry(
                user_id=self.test_user.user_id,
                mood_score=score,
                entry_date=test_date
            )

        # Получаем статистику
        stats = self.db.get_mood_stats(
            self.test_user.user_id,
            start_date=test_date,
            end_date=test_date
        )

        # Проверяем статистику
        self.assertEqual(stats.total_entries, 7)
        self.assertEqual(stats.average_score, 3.29)  # (1+3+5+4+2+5+3)/7
        self.assertEqual(stats.best_day_score, 5)
        self.assertEqual(stats.worst_day_score, 1)

        print("✅ Статистика настроения успешно рассчитана!")


class TestHelpers(unittest.TestCase):
    """Тесты для вспомогательных функций"""

    def test_format_mood_entry(self):
        """Тест форматирования записи настроения"""
        print("🧪 Тестируем форматирование записи настроения...")

        # Создаем тестовую запись
        mock_entry = Mock()
        mock_entry.mood_score = 4
        mock_entry.entry_date = date.today()
        mock_entry.created_at = datetime.now()
        mock_entry.note = "Тестовая заметка"
        mock_entry.tags = ["работа", "спорт"]

        # Форматируем запись
        formatted = format_mood_entry(mock_entry)

        # Проверяем результат
        self.assertIn("🙂 Хорошо", formatted)
        self.assertIn("Тестовая заметка", formatted)
        self.assertIn("работа", formatted)
        self.assertIn("спорт", formatted)

        print("✅ Запись настроения успешно отформатирована!")

    def test_config_constants(self):
        """Тест констант конфигурации"""
        print("🧪 Тестируем константы конфигурации...")

        # Проверяем эмодзи настроений
        self.assertEqual(config.MOOD_EMOJIS[1], "😢")
        self.assertEqual(config.MOOD_EMOJIS[5], "😊")

        # Проверяем названия настроений
        self.assertEqual(config.MOOD_NAMES[1], "Очень плохо")
        self.assertEqual(config.MOOD_NAMES[5], "Отлично")

        # Проверяем лимиты
        self.assertEqual(config.DIARY_TEXT_LIMIT, 500)

        print("✅ Константы конфигурации корректны!")


class TestKeyboards(unittest.TestCase):
    """Тесты для клавиатур"""

    def test_main_menu_keyboard(self):
        """Тест главной клавиатуры меню"""
        print("🧪 Тестируем главную клавиатуру меню...")

        keyboard = get_main_menu_keyboard()

        # Проверяем, что клавиатура создана
        self.assertIsNotNone(keyboard)
        self.assertIsNotNone(keyboard.inline_keyboard)

        # Проверяем количество кнопок
        buttons = []
        for row in keyboard.inline_keyboard:
            buttons.extend(row)

        # Должно быть 5 кнопок в главной клавиатуре
        self.assertEqual(len(buttons), 5)

        # Проверяем callback_data кнопок
        callback_datas = [btn.callback_data for btn in buttons]
        expected_callbacks = [
            "mood_record",
            "diary_menu",
            "tags_menu",
            "analytics_menu",
            "settings_menu"
        ]

        for expected in expected_callbacks:
            self.assertIn(expected, callback_datas)

        print("✅ Главная клавиатура меню корректна!")


class TestModels(unittest.TestCase):
    """Тесты для моделей данных"""

    def test_user_model(self):
        """Тест модели пользователя"""
        print("🧪 Тестируем модель пользователя...")

        # Создаем пользователя
        user = User(
            user_id=123456,
            username="testuser",
            first_name="Test User",
            timezone="UTC+3",
            reminder_time="21:00",
            reminder_enabled=True
        )

        # Проверяем поля
        self.assertEqual(user.user_id, 123456)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.first_name, "Test User")
        self.assertEqual(user.timezone, "UTC+3")
        self.assertEqual(user.reminder_time, "21:00")
        self.assertTrue(user.reminder_enabled)

        print("✅ Модель пользователя корректна!")

    def test_mood_entry_model(self):
        """Тест модели записи настроения"""
        print("🧪 Тестируем модель записи настроения...")

        # Создаем запись
        entry = MoodEntry(
            user_id=123456,
            mood_score=4,
            note="Тестовая запись",
            entry_date=date.today(),
            created_at=datetime.now()
        )

        # Проверяем поля
        self.assertEqual(entry.user_id, 123456)
        self.assertEqual(entry.mood_score, 4)
        self.assertEqual(entry.note, "Тестовая запись")
        self.assertEqual(entry.entry_date, date.today())

        print("✅ Модель записи настроения корректна!")

    def test_tag_model(self):
        """Тест модели тега"""
        print("🧪 Тестируем модель тега...")

        # Создаем тег
        tag = Tag(
            name="работа",
            category="Активность",
            user_id=123456,
            color="#FF5733"
        )

        # Проверяем поля
        self.assertEqual(tag.name, "работа")
        self.assertEqual(tag.category, "Активность")
        self.assertEqual(tag.user_id, 123456)
        self.assertEqual(tag.color, "#FF5733")

        print("✅ Модель тега корректна!")


def run_tests():
    """Запуск всех тестов с подробным выводом"""
    print("\n" + "="*60)
    print("🚀 ЗАПУСК ТЕСТОВ MOODTRACKER BOT")
    print("="*60)

    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавляем все тесты
    suite.addTest(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTest(loader.loadTestsFromTestCase(TestHelpers))
    suite.addTest(loader.loadTestsFromTestCase(TestKeyboards))
    suite.addTest(loader.loadTestsFromTestCase(TestModels))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)

    if result.wasSuccessful():
        print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print(f"📈 Запущено тестов: {result.testsRun}")
        print(f"❌ Ошибок: {len(result.errors)}")
        print(f"⚠️  Предупреждений: {len(result.failures)}")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
        print(f"📈 Запущено тестов: {result.testsRun}")
        print(f"❌ Ошибок: {len(result.errors)}")
        print(f"⚠️  Предупреждений: {len(result.failures)}")

        if result.errors:
            print("\n🔴 ОШИБКИ:")
            for test, error in result.errors:
                print(f"  • {test}: {error}")

        if result.failures:
            print("\n🟡 ПРОВАЛЫ:")
            for test, failure in result.failures:
                print(f"  • {test}: {failure}")

    print("="*60)
    return result.wasSuccessful()


if __name__ == "__main__":
    """Запуск тестов при прямом вызове файла"""
    success = run_tests()
    sys.exit(0 if success else 1)
