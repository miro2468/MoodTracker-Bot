import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from io import BytesIO

from database.models import MoodEntry
from config import config

# Настройка стиля графиков
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ChartGenerator:
    """Генератор графиков для аналитики настроения"""

    def __init__(self):
        self.colors = config.CHART_COLORS

    def generate_mood_trend_chart(self, entries: List[MoodEntry],
                                start_date: date, end_date: date) -> BytesIO:
        """Генерировать график тренда настроения"""
        if not entries:
            return self._create_empty_chart("Нет данных для отображения")

        # Подготовка данных
        df = pd.DataFrame([{
            'date': entry.entry_date,
            'mood': entry.mood_score,
            'diary': bool(entry.diary_text)
        } for entry in entries])

        df = df.sort_values('date')
        df['date'] = pd.to_datetime(df['date'])

        # Создание графика
        fig, ax = plt.subplots(figsize=(12, 6))

        # Линия тренда настроения
        ax.plot(df['date'], df['mood'], 'o-', color=self.colors['good'],
               linewidth=2, markersize=6, alpha=0.8, label='Настроение')

        # Точки с дневниковыми записями
        diary_points = df[df['diary']]
        if not diary_points.empty:
            ax.scatter(diary_points['date'], diary_points['mood'],
                      color=self.colors['excellent'], s=80, marker='*',
                      label='С дневником', zorder=5)

        # Настройка осей
        ax.set_ylim(0.5, 5.5)
        ax.set_yticks(range(1, 6))
        ax.set_yticklabels([f"{config.MOOD_EMOJIS[i]} {i}" for i in range(1, 6)])

        ax.set_title('📈 Тренд настроения', fontsize=16, pad=20)
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Настроение', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Форматирование дат
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # Сохранение в BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def generate_weekday_stats_chart(self, entries: List[MoodEntry]) -> BytesIO:
        """Генерировать статистику по дням недели"""
        if not entries:
            return self._create_empty_chart("Нет данных для анализа")

        # Подготовка данных
        df = pd.DataFrame([{
            'weekday': entry.entry_date.weekday(),
            'mood': entry.mood_score
        } for entry in entries])

        # Группировка по дням недели
        weekday_stats = df.groupby('weekday').agg({
            'mood': ['mean', 'count', 'std']
        }).round(2)

        weekday_stats.columns = ['mean_mood', 'count', 'std']
        weekday_stats = weekday_stats.reset_index()

        # Названия дней недели
        weekday_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        weekday_stats['weekday_name'] = weekday_stats['weekday'].map(
            lambda x: weekday_names[x]
        )

        # Создание графика
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # График среднего настроения
        bars1 = ax1.bar(weekday_stats['weekday_name'], weekday_stats['mean_mood'],
                       color=[self.get_mood_color(mood) for mood in weekday_stats['mean_mood']])
        ax1.set_title('📅 Среднее настроение по дням недели', fontsize=14)
        ax1.set_ylabel('Среднее настроение')
        ax1.set_ylim(0, 5.5)
        ax1.grid(True, alpha=0.3)

        # Добавление значений на столбцы
        for bar, mean_mood in zip(bars1, weekday_stats['mean_mood']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{mean_mood:.1f}', ha='center', va='bottom', fontsize=10)

        # График количества записей
        bars2 = ax2.bar(weekday_stats['weekday_name'], weekday_stats['count'],
                       color='skyblue', alpha=0.7)
        ax2.set_title('Количество записей по дням недели', fontsize=14)
        ax2.set_ylabel('Количество записей')
        ax2.grid(True, alpha=0.3)

        # Добавление значений на столбцы
        for bar, count in zip(bars2, weekday_stats['count']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(int(count)), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()

        # Сохранение в BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def generate_tags_pie_chart(self, tag_stats: Dict[str, int]) -> BytesIO:
        """Генерировать круговую диаграмму по тегам"""
        if not tag_stats:
            return self._create_empty_chart("Нет данных о тегах")

        # Сортировка по количеству
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)

        # Ограничение до топ 10
        if len(sorted_tags) > 10:
            top_tags = dict(sorted_tags[:9])
            other_count = sum(count for _, count in sorted_tags[9:])
            top_tags['Другие'] = other_count
        else:
            top_tags = dict(sorted_tags)

        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 8))

        # Цвета для тегов
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_tags)))

        wedges, texts, autotexts = ax.pie(
            top_tags.values(),
            labels=top_tags.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10}
        )

        ax.set_title('🏷️ Распределение тегов', fontsize=16, pad=20)

        # Улучшение отображения процентов
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        plt.tight_layout()

        # Сохранение в BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def generate_heatmap_chart(self, entries: List[MoodEntry]) -> BytesIO:
        """Генерировать тепловую карту настроения по часам"""
        if not entries:
            return self._create_empty_chart("Нет данных для тепловой карты")

        # Подготовка данных
        data = []
        for entry in entries:
            if entry.created_at:
                hour = entry.created_at.hour
                weekday = entry.created_at.weekday()
                data.append({
                    'hour': hour,
                    'weekday': weekday,
                    'mood': entry.mood_score
                })

        if not data:
            return self._create_empty_chart("Недостаточно данных для анализа по времени")

        df = pd.DataFrame(data)

        # Создание сводной таблицы
        pivot_table = df.pivot_table(
            values='mood',
            index='weekday',
            columns='hour',
            aggfunc='mean'
        ).round(1)

        # Заполнение пропущенных значений средним
        pivot_table = pivot_table.fillna(df['mood'].mean())

        # Названия дней недели
        weekday_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

        # Создание тепловой карты
        fig, ax = plt.subplots(figsize=(12, 6))

        sns.heatmap(
            pivot_table,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=3.0,
            vmin=1,
            vmax=5,
            ax=ax,
            cbar_kws={'label': 'Настроение'}
        )

        ax.set_title('🔥 Тепловая карта настроения по времени', fontsize=16, pad=20)
        ax.set_xlabel('Час дня', fontsize=12)
        ax.set_ylabel('День недели', fontsize=12)
        ax.set_yticklabels(weekday_names, rotation=0)

        plt.tight_layout()

        # Сохранение в BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def generate_mood_distribution_chart(self, entries: List[MoodEntry]) -> BytesIO:
        """Генерировать гистограмму распределения настроения"""
        if not entries:
            return self._create_empty_chart("Нет данных для анализа")

        # Подготовка данных
        moods = [entry.mood_score for entry in entries]
        mood_counts = pd.Series(moods).value_counts().sort_index()

        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(
            mood_counts.index,
            mood_counts.values,
            color=[self.get_mood_color(score) for score in mood_counts.index]
        )

        ax.set_title('📊 Распределение настроения', fontsize=16, pad=20)
        ax.set_xlabel('Оценка настроения', fontsize=12)
        ax.set_ylabel('Количество записей', fontsize=12)
        ax.set_xticks(range(1, 6))
        ax.set_xticklabels([f"{config.MOOD_EMOJIS[i]} {i}" for i in range(1, 6)])
        ax.grid(True, alpha=0.3)

        # Добавление значений на столбцы
        for bar, count in zip(bars, mood_counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   str(count), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()

        # Сохранение в BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def get_mood_color(self, score: float) -> str:
        """Получить цвет для оценки настроения"""
        return config.CHART_COLORS.get('neutral', '#FFEB3B')

    def _create_empty_chart(self, message: str) -> BytesIO:
        """Создать пустой график с сообщением"""
        fig, ax = plt.subplots(figsize=(8, 6))

        ax.text(0.5, 0.5, message,
               transform=ax.transAxes,
               ha='center', va='center',
               fontsize=14, color='gray')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Сохранение в BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

# Глобальный экземпляр генератора графиков
chart_generator = ChartGenerator()
