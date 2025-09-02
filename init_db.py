#!/usr/bin/env python3
"""
Скрипт инициализации базы данных SQLite для ULE Platform
"""

from app.database import create_tables
import os

def init_database():
    """Создает все таблицы в базе данных"""
    print("🗄️ Инициализация базы данных SQLite...")
    
    # Создаем все таблицы
    create_tables()
    
    print("✅ База данных успешно инициализирована!")
    print(f"📁 Файл базы данных: {os.path.abspath('ule_platform.db')}")
    
    # Проверяем, что файл создался
    if os.path.exists('ule_platform.db'):
        file_size = os.path.getsize('ule_platform.db')
        print(f"📊 Размер файла: {file_size} байт")

if __name__ == "__main__":
    init_database()
