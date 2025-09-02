#!/usr/bin/env python3
"""
Тестовый скрипт для проверки базы данных
"""

import sqlite3
import os

def test_database():
    """Тестирует базу данных"""
    db_path = "ule_platform.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        print("Создаем новую базу данных...")
        
        # Создаем простую базу данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу users
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                city TEXT,
                role TEXT DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу service_offers
        cursor.execute('''
            CREATE TABLE service_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                performer_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                hourly_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (performer_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ База данных создана!")
    
    # Тестируем подключение
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Таблицы: {[table[0] for table in tables]}")
        
        # Проверяем таблицу service_offers
        if ('service_offers',) in tables:
            cursor.execute("PRAGMA table_info(service_offers)")
            columns = cursor.fetchall()
            print(f"📝 Структура service_offers:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("✅ База данных работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании базы данных: {e}")

if __name__ == "__main__":
    test_database()
