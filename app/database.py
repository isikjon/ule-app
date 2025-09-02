import sqlite3
import os
from contextlib import contextmanager

# Путь к базе данных
DATABASE_PATH = "ule_platform.db"

@contextmanager
def get_db():
    """Контекстный менеджер для подключения к базе данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    # Убираем row_factory, так как он может вызывать проблемы
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    """Создание всех таблиц в базе данных"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                surname TEXT,
                patronymic TEXT,
                email TEXT,
                date_of_birth TEXT,
                city TEXT,
                role TEXT DEFAULT 'customer',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                address TEXT NOT NULL,
                date TEXT NOT NULL,
                price REAL NOT NULL,
                photos TEXT,
                status TEXT DEFAULT 'open',
                customer_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица предложений услуг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                performer_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                hourly_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (performer_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица откликов на проекты
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                performer_id INTEGER NOT NULL,
                offer_price REAL NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (performer_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Создаем индексы для производительности
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_customer ON tasks(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_task ON project_responses(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
        
        conn.commit()
        print("✅ Таблицы базы данных созданы успешно!")
