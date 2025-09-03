import sqlite3
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import User, MoodEntry, Tag, MoodTag, UserSettings, MoodStats, MoodPattern
from config import config, logger

class DatabaseManager:
    """Менеджер базы данных для MoodTracker Bot"""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Создание таблицы пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    timezone TEXT DEFAULT 'UTC+3'
                )
            ''')

            # Создание таблицы записей настроения
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    mood_score INTEGER CHECK(mood_score >= 1 AND mood_score <= 5),
                    diary_text TEXT,
                    entry_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Создание таблицы тегов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    category TEXT,
                    is_predefined BOOLEAN DEFAULT FALSE,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES users (user_id)
                )
            ''')

            # Создание связующей таблицы записей и тегов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_tags (
                    mood_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (mood_id, tag_id),
                    FOREIGN KEY (mood_id) REFERENCES mood_entries (id),
                    FOREIGN KEY (tag_id) REFERENCES tags (id)
                )
            ''')

            # Создание таблицы настроек пользователя
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    daily_reminder BOOLEAN DEFAULT TRUE,
                    reminder_time TIME DEFAULT '21:00',
                    language TEXT DEFAULT 'ru',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Добавление предустановленных тегов
            self._add_predefined_tags(cursor)

            conn.commit()
            logger.info("База данных инициализирована успешно")

    def _add_predefined_tags(self, cursor):
        """Добавление предустановленных тегов"""
        for category, tags in config.PREDEFINED_TAGS.items():
            for tag in tags:
                cursor.execute('''
                    INSERT OR IGNORE INTO tags (name, category, is_predefined, created_by)
                    VALUES (?, ?, TRUE, NULL)
                ''', (tag, category))

    # ===== МЕТОДЫ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ =====

    def get_or_create_user(self, user_id: int, username: str = None,
                          first_name: str = None) -> User:
        """Получить или создать пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем существует ли пользователь
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()

            if row:
                return User(
                    user_id=row['user_id'],
                    username=row['username'],
                    first_name=row['first_name'],
                    registration_date=datetime.fromisoformat(row['registration_date']),
                    timezone=row['timezone']
                )

            # Создаем нового пользователя
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))

            # Создаем настройки по умолчанию
            cursor.execute('''
                INSERT INTO user_settings (user_id)
                VALUES (?)
            ''', (user_id,))

            conn.commit()

            return User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                registration_date=datetime.now(),
                timezone=config.DEFAULT_TIMEZONE
            )

    def update_user_timezone(self, user_id: int, timezone: str):
        """Обновить часовой пояс пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET timezone = ? WHERE user_id = ?
            ''', (timezone, user_id))
            conn.commit()

    # ===== МЕТОДЫ РАБОТЫ С НАСТРОЕНИЕМ =====

    def save_mood_entry(self, entry: MoodEntry, tag_ids: List[int] = None) -> int:
        """Сохранить запись настроения"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Сохраняем запись настроения
            cursor.execute('''
                INSERT INTO mood_entries (user_id, mood_score, diary_text, entry_date)
                VALUES (?, ?, ?, ?)
            ''', (
                entry.user_id,
                entry.mood_score,
                entry.diary_text,
                entry.entry_date or date.today()
            ))

            mood_id = cursor.lastrowid

            # Добавляем теги
            if tag_ids:
                for tag_id in tag_ids:
                    cursor.execute('''
                        INSERT INTO mood_tags (mood_id, tag_id)
                        VALUES (?, ?)
                    ''', (mood_id, tag_id))

            conn.commit()
            return mood_id

    def get_mood_entries(self, user_id: int, start_date: date = None,
                        end_date: date = None, limit: int = None) -> List[MoodEntry]:
        """Получить записи настроения за период"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT * FROM mood_entries
                WHERE user_id = ?
            '''
            params = [user_id]

            if start_date:
                query += ' AND entry_date >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND entry_date <= ?'
                params.append(end_date)

            query += ' ORDER BY entry_date DESC, created_at DESC'

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            entries = []
            for row in rows:
                entry = MoodEntry(
                    id=row['id'],
                    user_id=row['user_id'],
                    mood_score=row['mood_score'],
                    diary_text=row['diary_text'],
                    entry_date=date.fromisoformat(row['entry_date']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                entries.append(entry)

            return entries

    def get_today_mood(self, user_id: int) -> Optional[MoodEntry]:
        """Получить запись настроения за сегодня"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM mood_entries
                WHERE user_id = ? AND entry_date = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id, date.today()))

            row = cursor.fetchone()
            if row:
                return MoodEntry(
                    id=row['id'],
                    user_id=row['user_id'],
                    mood_score=row['mood_score'],
                    diary_text=row['diary_text'],
                    entry_date=date.fromisoformat(row['entry_date']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None

    # ===== МЕТОДЫ РАБОТЫ С ТЕГАМИ =====

    def get_all_tags(self, user_id: int = None) -> List[Tag]:
        """Получить все теги (предустановленные + пользовательские)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                    SELECT * FROM tags
                    WHERE is_predefined = TRUE OR created_by = ?
                    ORDER BY category, name
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT * FROM tags
                    ORDER BY category, name
                ''')

            rows = cursor.fetchall()
            tags = []

            for row in rows:
                tag = Tag(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    is_predefined=bool(row['is_predefined']),
                    created_by=row['created_by']
                )
                tags.append(tag)

            return tags

    def create_custom_tag(self, name: str, category: str, user_id: int) -> int:
        """Создать пользовательский тег"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tags (name, category, is_predefined, created_by)
                VALUES (?, ?, FALSE, ?)
            ''', (name, category, user_id))

            conn.commit()
            return cursor.lastrowid

    def delete_custom_tag(self, tag_id: int, user_id: int) -> bool:
        """Удалить пользовательский тег"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем, что тег создан этим пользователем и не является предустановленным
            cursor.execute('''
                SELECT id FROM tags
                WHERE id = ? AND created_by = ? AND is_predefined = FALSE
            ''', (tag_id, user_id))

            if cursor.fetchone():
                # Удаляем связи с записями
                cursor.execute('DELETE FROM mood_tags WHERE tag_id = ?', (tag_id,))
                # Удаляем тег
                cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
                conn.commit()
                return True

            return False

    # ===== МЕТОДЫ АНАЛИТИКИ =====

    def get_mood_stats(self, user_id: int, start_date: date,
                      end_date: date) -> MoodStats:
        """Получить статистику настроения за период"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Основная статистика
            cursor.execute('''
                SELECT
                    COUNT(*) as total_entries,
                    AVG(mood_score) as avg_mood,
                    MAX(mood_score) as max_mood,
                    MIN(mood_score) as min_mood
                FROM mood_entries
                WHERE user_id = ? AND entry_date BETWEEN ? AND ?
            ''', (user_id, start_date, end_date))

            stats_row = cursor.fetchone()

            if not stats_row or stats_row['total_entries'] == 0:
                return MoodStats(
                    period=f"{start_date} - {end_date}",
                    average_mood=0.0,
                    total_entries=0
                )

            # Лучший и худший день
            cursor.execute('''
                SELECT entry_date, AVG(mood_score) as avg_mood
                FROM mood_entries
                WHERE user_id = ? AND entry_date BETWEEN ? AND ?
                GROUP BY entry_date
                ORDER BY avg_mood DESC
                LIMIT 1
            ''', (user_id, start_date, end_date))

            best_day_row = cursor.fetchone()
            best_day = best_day_row['entry_date'] if best_day_row else None

            cursor.execute('''
                SELECT entry_date, AVG(mood_score) as avg_mood
                FROM mood_entries
                WHERE user_id = ? AND entry_date BETWEEN ? AND ?
                GROUP BY entry_date
                ORDER BY avg_mood ASC
                LIMIT 1
            ''', (user_id, start_date, end_date))

            worst_day_row = cursor.fetchone()
            worst_day = worst_day_row['entry_date'] if worst_day_row else None

            # Самые частые теги
            cursor.execute('''
                SELECT t.name, COUNT(mt.mood_id) as count
                FROM mood_tags mt
                JOIN tags t ON mt.tag_id = t.id
                JOIN mood_entries me ON mt.mood_id = me.id
                WHERE me.user_id = ? AND me.entry_date BETWEEN ? AND ?
                GROUP BY t.id, t.name
                ORDER BY count DESC
                LIMIT 5
            ''', (user_id, start_date, end_date))

            frequent_tags = [(row['name'], row['count']) for row in cursor.fetchall()]

            return MoodStats(
                period=f"{start_date} - {end_date}",
                average_mood=round(stats_row['avg_mood'], 1),
                total_entries=stats_row['total_entries'],
                best_day=best_day,
                worst_day=worst_day,
                most_frequent_tags=frequent_tags
            )

    def get_mood_patterns(self, user_id: int, min_entries: int = 5) -> List[MoodPattern]:
        """Получить паттерны настроения (корреляция тегов с настроением)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    t.name,
                    COUNT(CASE WHEN me.mood_score >= 4 THEN 1 END) as positive_entries,
                    COUNT(me.id) as total_entries,
                    AVG(me.mood_score) as avg_mood_with_tag,
                    (SELECT AVG(mood_score) FROM mood_entries WHERE user_id = ?) as overall_avg
                FROM mood_tags mt
                JOIN tags t ON mt.tag_id = t.id
                JOIN mood_entries me ON mt.mood_id = me.id
                WHERE me.user_id = ?
                GROUP BY t.id, t.name
                HAVING COUNT(me.id) >= ?
                ORDER BY ABS(AVG(me.mood_score) - (SELECT AVG(mood_score) FROM mood_entries WHERE user_id = ?)) DESC
            ''', (user_id, user_id, min_entries, user_id))

            patterns = []
            for row in cursor.fetchall():
                correlation = row['avg_mood_with_tag'] - row['overall_avg']
                pattern = MoodPattern(
                    tag_name=row['name'],
                    correlation=round(correlation, 2),
                    positive_entries=row['positive_entries'],
                    total_entries=row['total_entries']
                )
                patterns.append(pattern)

            return patterns

    # ===== МЕТОДЫ НАСТРОЕК =====

    def get_user_settings(self, user_id: int) -> UserSettings:
        """Получить настройки пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()

            if row:
                return UserSettings(
                    user_id=row['user_id'],
                    daily_reminder=bool(row['daily_reminder']),
                    reminder_time=time.fromisoformat(row['reminder_time']),
                    language=row['language']
                )

            # Возвращаем настройки по умолчанию
            return UserSettings(user_id=user_id)

    def update_user_settings(self, settings: UserSettings):
        """Обновить настройки пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_settings
                SET daily_reminder = ?, reminder_time = ?, language = ?
                WHERE user_id = ?
            ''', (
                settings.daily_reminder,
                settings.reminder_time.isoformat(),
                settings.language,
                settings.user_id
            ))
            conn.commit()

    # ===== СЕРВИСНЫЕ МЕТОДЫ =====

    def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Экспорт данных пользователя для CSV/PDF"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Получаем все записи настроения с тегами
            cursor.execute('''
                SELECT
                    me.entry_date,
                    me.mood_score,
                    me.diary_text,
                    GROUP_CONCAT(t.name, ', ') as tags
                FROM mood_entries me
                LEFT JOIN mood_tags mt ON me.id = mt.mood_id
                LEFT JOIN tags t ON mt.tag_id = t.id
                WHERE me.user_id = ?
                GROUP BY me.id
                ORDER BY me.entry_date DESC
            ''', (user_id,))

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'date': row['entry_date'],
                    'mood_score': row['mood_score'],
                    'mood_name': config.MOOD_NAMES[row['mood_score']],
                    'diary_text': row['diary_text'] or '',
                    'tags': row['tags'] or ''
                })

            return {
                'user_id': user_id,
                'export_date': datetime.now().isoformat(),
                'total_entries': len(entries),
                'entries': entries
            }

# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()
