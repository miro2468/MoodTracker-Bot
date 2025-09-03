# 🚀 Деплой и запуск MoodTracker Bot

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
```bash
# Создайте файл .env
cp .env.example .env

# Отредактируйте .env и добавьте ваш токен бота
BOT_TOKEN=ваш_токен_от_BotFather
```

### 3. Запуск бота
```bash
# Рекомендуемый способ запуска
python run.py

# Или напрямую
python bot.py
```

## 📋 Предварительные требования

### Системные требования
- **Python**: 3.8 или выше
- **Операционная система**: Windows, Linux, macOS
- **Память**: минимум 256 MB RAM
- **Диск**: минимум 50 MB свободного места

### Получение токена бота
1. Перейдите к [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## 🛠️ Установка

### Автоматическая установка (Windows)
```batch
# Клонирование репозитория
git clone <repository-url>
cd mood-tracker-bot

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### Автоматическая установка (Linux/macOS)
```bash
# Клонирование репозитория
git clone <repository-url>
cd mood-tracker-bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Ручная установка зависимостей
```bash
pip install aiogram==3.0.0
pip install matplotlib==3.7.1
pip install seaborn==0.12.2
pip install pandas==2.0.3
pip install numpy==1.24.3
pip install python-dotenv==1.0.0
pip install apscheduler==3.10.4
pip install Pillow==10.0.0
pip install reportlab==4.0.4
```

## ⚙️ Конфигурация

### Файл .env
```env
# Токен бота Telegram
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
```

### Основные настройки (config.py)
```python
# Лимиты
DIARY_TEXT_LIMIT = 500          # Максимум символов в дневнике
MAX_CUSTOM_TAGS = 50           # Максимум пользовательских тегов

# Время по умолчанию
DEFAULT_REMINDER_TIME = "21:00"  # Время ежедневных напоминаний
DEFAULT_TIMEZONE = "UTC+3"      # Часовой пояс по умолчанию

# База данных
DATABASE_PATH = 'mood_tracker.db'  # Путь к файлу базы данных
```

## 🚀 Запуск

### Режим разработки
```bash
# С подробным логированием
python run.py

# Или с логированием в файл
python bot.py 2>&1 | tee bot.log
```

### Фоновый режим (Linux/macOS)
```bash
# Запуск в фоне
nohup python run.py &

# Проверка статуса
ps aux | grep python

# Остановка
pkill -f "python run.py"
```

### Фоновый режим (Windows)
```batch
# Запуск в фоне (PowerShell)
Start-Process -NoNewWindow python run.py

# Или с помощью screen (если установлен)
python run.py
```

## 📊 Мониторинг

### Логи
Бот ведет подробные логи в:
- Консоль (при запуске)
- Файл `bot.log` (все сообщения)

### Проверка работоспособности
```bash
# Проверка запущенных процессов
ps aux | grep python

# Проверка логов
tail -f bot.log

# Проверка базы данных
ls -la mood_tracker.db
```

### Статистика бота
```python
# В Python консоли
from database.db_manager import db_manager
from fixes import get_bot_statistics

stats = get_bot_statistics()
print(stats)
```

## 🔧 Обслуживание

### Резервное копирование
```bash
# Создание резервной копии базы данных
cp mood_tracker.db backup_$(date +%Y%m%d_%H%M%S).db

# Или с помощью Python
python -c "from fixes import BotFixes; BotFixes.backup_database()"
```

### Очистка старых данных
```python
# Очистка данных старше 1 года
from fixes import BotFixes
BotFixes.cleanup_old_data(days=365)
```

### Оптимизация базы данных
```python
# Оптимизация производительности
from fixes import BotFixes
BotFixes.optimize_database()
```

## 🐛 Устранение неисправностей

### Проблема: "Module not found"
```bash
# Переустановка зависимостей
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Проблема: "BOT_TOKEN invalid"
1. Проверьте токен в файле `.env`
2. Убедитесь, что токен получен от @BotFather
3. Проверьте, что бот не заблокирован в Telegram

### Проблема: "Database locked"
```bash
# Удаление блокировки
rm -f mood_tracker.db-lock

# Или перезапуск бота
```

### Проблема: Высокое потребление памяти
```python
# Очистка кэша matplotlib
import matplotlib.pyplot as plt
plt.close('all')
```

## 📈 Производительность

### Оптимизация для большого количества пользователей
1. **Индексы базы данных**: автоматически создаются
2. **Кэширование графиков**: графики кэшируются на 1 час
3. **Очистка памяти**: автоматическая очистка после операций

### Рекомендации по хостингу
- **RAM**: 512 MB минимум
- **CPU**: 1 ядро минимум
- **Disk**: SSD для лучшей производительности
- **Network**: Стабильное интернет-соединение

## 🔄 Обновление

### Обновление кода
```bash
# Получение обновлений
git pull origin main

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Перезапуск бота
python run.py
```

### Миграция базы данных
```python
# При изменении структуры БД
from database.db_manager import db_manager

# Создание новой базы данных
db_manager.init_database()
```

## 🌐 Веб-интерфейс (опционально)

### Запуск с веб-интерфейсом
```bash
# Установка дополнительных зависимостей
pip install flask

# Запуск веб-сервера
python web_app.py
```

## 📞 Поддержка

### Логи отладки
```bash
# Включение подробного логирования
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import bot
"
```

### Создание issue
При возникновении проблем:
1. Соберите логи: `tail -100 bot.log`
2. Опишите проблему с шагами воспроизведения
3. Укажите версию Python и ОС

---

## ✅ Проверка установки

Запустите эту команду для проверки корректности установки:
```bash
python -c "
import sys
print('Python version:', sys.version)
import aiogram, matplotlib, pandas, seaborn
print('All dependencies: OK')
from config import config
print('Config loaded successfully')
print('✅ Installation check passed!')
"
```

## 🎯 Быстрые команды

```bash
# Полная проверка
python run.py --check

# Запуск с профилированием
python -m cProfile run.py

# Очистка кэша
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```
