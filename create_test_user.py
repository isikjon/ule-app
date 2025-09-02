#!/usr/bin/env python3
"""
Скрипт для создания тестового пользователя
"""

from app.database import create_tables, get_db
from app.auth.service import hash_password, format_russian_phone

def create_test_user():
    """Создает тестового пользователя"""
    print("🗄️ Инициализация базы данных...")
    create_tables()
    
    test_phone = "+7 (999) 123-45-67"
    test_password = "123456"
    test_name = "Тест Пользователь"
    test_city = "Бишкек"
    
    formatted_phone = format_russian_phone(test_phone)
    password_hash = hash_password(test_password)
    
    print(f"Создание тестового пользователя:")
    print(f"Телефон: {formatted_phone}")
    print(f"Пароль: {test_password}")
    print(f"Имя: {test_name}")
    print(f"Город: {test_city}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE phone = ?", (formatted_phone,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"❌ Пользователь уже существует: {formatted_phone}")
            return
        
        # Создаем нового пользователя
        cursor.execute("""
            INSERT INTO users (phone, password_hash, name, city, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'customer', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (formatted_phone, password_hash, test_name, test_city))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Тестовый пользователь создан успешно!")
        print(f"User ID: {user_id}")
        print(f"Для входа используйте:")
        print(f"  Телефон: {test_phone}")
        print(f"  Пароль: {test_password}")

if __name__ == "__main__":
    create_test_user()
