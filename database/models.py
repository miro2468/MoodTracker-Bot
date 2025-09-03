from datetime import datetime, date, time
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class User:
    """Модель пользователя"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    registration_date: Optional[datetime] = None
    timezone: str = "UTC+3"

@dataclass
class MoodEntry:
    """Модель записи настроения"""
    id: Optional[int] = None
    user_id: int = 0
    mood_score: int = 3
    diary_text: Optional[str] = None
    entry_date: Optional[date] = None
    created_at: Optional[datetime] = None

@dataclass
class Tag:
    """Модель тега"""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    is_predefined: bool = False
    created_by: Optional[int] = None

@dataclass
class MoodTag:
    """Связующая модель записи и тега"""
    mood_id: int
    tag_id: int

@dataclass
class UserSettings:
    """Модель настроек пользователя"""
    user_id: int
    daily_reminder: bool = True
    reminder_time: time = time(21, 0)  # 21:00
    language: str = "ru"

@dataclass
class MoodStats:
    """Статистика настроения"""
    period: str
    average_mood: float
    total_entries: int
    best_day: Optional[str] = None
    worst_day: Optional[str] = None
    most_frequent_tags: List[tuple[str, int]] = None

    def __post_init__(self):
        if self.most_frequent_tags is None:
            self.most_frequent_tags = []

@dataclass
class MoodPattern:
    """Паттерн настроения"""
    tag_name: str
    correlation: float
    positive_entries: int
    total_entries: int
