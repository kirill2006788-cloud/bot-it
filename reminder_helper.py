#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для управления напоминаниями и задачами
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ReminderHelper:
    """Класс для управления напоминаниями и задачами"""
    
    def __init__(self, data_file: str = "reminders.json"):
        self.data_file = data_file
        self.reminders: Dict[int, List[Dict]] = {}  # user_id -> список напоминаний
        self.tasks: Dict[int, List[Dict]] = {}  # user_id -> список задач
        self.load_data()
    
    def load_data(self):
        """Загрузить данные из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reminders = {int(k): v for k, v in data.get('reminders', {}).items()}
                    self.tasks = {int(k): v for k, v in data.get('tasks', {}).items()}
                logger.info(f"Загружено {sum(len(v) for v in self.reminders.values())} напоминаний и {sum(len(v) for v in self.tasks.values())} задач")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            self.reminders = {}
            self.tasks = {}
    
    def save_data(self):
        """Сохранить данные в файл"""
        try:
            data = {
                'reminders': self.reminders,
                'tasks': self.tasks
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
    
    def parse_time(self, time_str: str) -> Optional[datetime]:
        """
        Парсинг времени из строки
        Поддерживает:
        - "через 30 минут"
        - "через 2 часа"
        - "в 15:30"
        - "завтра в 10:00"
        - "через 1 день"
        """
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        # "через X минут"
        match = re.search(r'через\s+(\d+)\s+минут', time_str)
        if match:
            minutes = int(match.group(1))
            return now + timedelta(minutes=minutes)
        
        # "через X часов"
        match = re.search(r'через\s+(\d+)\s+час', time_str)
        if match:
            hours = int(match.group(1))
            return now + timedelta(hours=hours)
        
        # "через X дней"
        match = re.search(r'через\s+(\d+)\s+дн', time_str)
        if match:
            days = int(match.group(1))
            return now + timedelta(days=days)
        
        # "в HH:MM"
        match = re.search(r'в\s+(\d{1,2}):(\d{2})', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target < now:
                target += timedelta(days=1)  # Если время прошло, то завтра
            return target
        
        # "завтра в HH:MM"
        match = re.search(r'завтра\s+в\s+(\d{1,2}):(\d{2})', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            target = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            return target
        
        # "через X часов Y минут"
        match = re.search(r'через\s+(\d+)\s+час.*?(\d+)\s+минут', time_str)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return now + timedelta(hours=hours, minutes=minutes)
        
        return None
    
    def add_reminder(self, user_id: int, text: str, time_str: str) -> Optional[Dict]:
        """Добавить напоминание"""
        try:
            reminder_time = self.parse_time(time_str)
            if not reminder_time:
                return None
            
            reminder = {
                'id': len(self.reminders.get(user_id, [])) + 1,
                'text': text,
                'time': reminder_time.isoformat(),
                'created_at': datetime.now().isoformat(),
                'sent': False
            }
            
            if user_id not in self.reminders:
                self.reminders[user_id] = []
            
            self.reminders[user_id].append(reminder)
            self.save_data()
            
            logger.info(f"Добавлено напоминание для пользователя {user_id}: {text} в {reminder_time}")
            return reminder
            
        except Exception as e:
            logger.error(f"Ошибка добавления напоминания: {e}")
            return None
    
    def add_task(self, user_id: int, text: str, priority: str = "normal") -> Dict:
        """Добавить задачу"""
        try:
            task = {
                'id': len(self.tasks.get(user_id, [])) + 1,
                'text': text,
                'priority': priority,  # low, normal, high
                'completed': False,
                'created_at': datetime.now().isoformat()
            }
            
            if user_id not in self.tasks:
                self.tasks[user_id] = []
            
            self.tasks[user_id].append(task)
            self.save_data()
            
            logger.info(f"Добавлена задача для пользователя {user_id}: {text}")
            return task
            
        except Exception as e:
            logger.error(f"Ошибка добавления задачи: {e}")
            return None
    
    def get_reminders(self, user_id: int, include_sent: bool = False) -> List[Dict]:
        """Получить список напоминаний пользователя"""
        reminders = self.reminders.get(user_id, [])
        if not include_sent:
            reminders = [r for r in reminders if not r.get('sent', False)]
        return sorted(reminders, key=lambda x: x.get('time', ''))
    
    def get_tasks(self, user_id: int, include_completed: bool = False) -> List[Dict]:
        """Получить список задач пользователя"""
        tasks = self.tasks.get(user_id, [])
        if not include_completed:
            tasks = [t for t in tasks if not t.get('completed', False)]
        return tasks
    
    def get_due_reminders(self) -> List[Dict]:
        """Получить все напоминания, которые должны быть отправлены"""
        due_reminders = []
        now = datetime.now()
        
        for user_id, reminders in self.reminders.items():
            for reminder in reminders:
                if reminder.get('sent', False):
                    continue
                
                try:
                    reminder_time = datetime.fromisoformat(reminder['time'])
                    if reminder_time <= now:
                        reminder['user_id'] = user_id
                        due_reminders.append(reminder)
                except Exception as e:
                    logger.error(f"Ошибка парсинга времени напоминания: {e}")
        
        return due_reminders
    
    def mark_reminder_sent(self, user_id: int, reminder_id: int):
        """Пометить напоминание как отправленное"""
        if user_id in self.reminders:
            for reminder in self.reminders[user_id]:
                if reminder.get('id') == reminder_id:
                    reminder['sent'] = True
                    self.save_data()
                    break
    
    def complete_task(self, user_id: int, task_id: int) -> bool:
        """Пометить задачу как выполненную"""
        if user_id in self.tasks:
            for task in self.tasks[user_id]:
                if task.get('id') == task_id:
                    task['completed'] = True
                    self.save_data()
                    return True
        return False
    
    def delete_task(self, user_id: int, task_id: int) -> bool:
        """Удалить задачу"""
        if user_id in self.tasks:
            self.tasks[user_id] = [t for t in self.tasks[user_id] if t.get('id') != task_id]
            self.save_data()
            return True
        return False
    
    def delete_reminder(self, user_id: int, reminder_id: int) -> bool:
        """Удалить напоминание"""
        if user_id in self.reminders:
            self.reminders[user_id] = [r for r in self.reminders[user_id] if r.get('id') != reminder_id]
            self.save_data()
            return True
        return False
    
    def format_reminder(self, reminder: Dict) -> str:
        """Форматировать напоминание для отображения"""
        try:
            reminder_time = datetime.fromisoformat(reminder['time'])
            time_str = reminder_time.strftime("%d.%m.%Y %H:%M")
            return f"⏰ {reminder['text']}\n📅 {time_str}"
        except:
            return f"⏰ {reminder['text']}"
    
    def format_task(self, task: Dict) -> str:
        """Форматировать задачу для отображения"""
        priority_emoji = {
            'low': '🟢',
            'normal': '🟡',
            'high': '🔴'
        }
        emoji = priority_emoji.get(task.get('priority', 'normal'), '🟡')
        status = "✅" if task.get('completed', False) else "⏳"
        return f"{status} {emoji} {task['text']}"

