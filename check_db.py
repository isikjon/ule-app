#!/usr/bin/env python3
"""
Скрипт для проверки базы данных
"""

import sqlite3
import os

def check_database():
    """Проверяет состояние базы данных"""
    db_path = "ule_platform.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существующие таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ База данных найдена: {db_path}")
        print(f"📊 Размер файла: {os.path.getsize(db_path)} байт")
        print(f"📋 Таблицы: {[table[0] for table in tables]}")
        
        # Проверяем таблицу service_offers
        if ('service_offers',) in tables:
            cursor.execute("SELECT COUNT(*) FROM service_offers")
            count = cursor.fetchone()[0]
            print(f"🔧 Записей в service_offers: {count}")
            
            # Проверяем структуру таблицы
            cursor.execute("PRAGMA table_info(service_offers)")
            columns = cursor.fetchall()
            print(f"📝 Структура service_offers:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False

if __name__ == "__main__":
    check_database()
