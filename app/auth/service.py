import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import jwt
import hashlib
from app.database import get_db

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def format_russian_phone(phone: str) -> str:
    print(f"Formatting phone: {phone}")
    digits = re.sub(r'\D', '', phone)
    print(f"Extracted digits: {digits}")

    if digits.startswith('7'):
        digits = '+' + digits
    elif digits.startswith('8'):
        digits = '+7' + digits[1:]

    if len(digits) == 12:
        formatted = f"+7 ({digits[2:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:12]}"
        print(f"Formatted result: {formatted}")
        return formatted
    print(f"Returning original: {phone}")
    return phone

def hash_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    print(f"Password hashed successfully, length: {len(hashed)}")
    return hashed

def verify_password(password: str, hashed: str) -> bool:
    result = hash_password(password) == hashed
    print(f"Password verification result: {result}")
    return result

def generate_sms_code(phone: str) -> str:
    print(f"Generating SMS code for phone: {phone}")
    return "1111"

def verify_sms_code(phone: str, code: str) -> bool:
    result = code == "1111"
    print(f"SMS code verification for phone {phone}: {code} == '1111' = {result}")
    return result

def create_access_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        print(f"Creating JWT token for data: {to_encode}")
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"JWT token created successfully")
        return encoded_jwt
    except Exception as e:
        print(f"Error creating JWT token: {str(e)}")
        raise e

def register_user(phone: str, password: str, name: str = None, city: str = None) -> dict:
    print(f"Registering user with phone: {phone}, name: {name}, city: {city}")
    formatted_phone = format_russian_phone(phone)
    print(f"Formatted phone for registration: {formatted_phone}")

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE phone = ?", (formatted_phone,))
        if cursor.fetchone():
            print(f"User already exists: {formatted_phone}")
            raise ValueError("User already exists")

        # Создаем нового пользователя
        cursor.execute("""
            INSERT INTO users (phone, password_hash, name, city, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'customer', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (formatted_phone, hash_password(password), name, city))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print(f"User registered successfully: {formatted_phone}")
        print(f"User ID: {user_id}")

    return {"success": True, "message": "User registered successfully"}

def authenticate_user(phone: str, password: str) -> Optional[dict]:
    print(f"Authenticating user with phone: {phone}")
    formatted_phone = format_russian_phone(phone)
    print(f"Formatted phone: {formatted_phone}")

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Ищем пользователя в базе данных
        cursor.execute("SELECT id, password_hash, name, city, role FROM users WHERE phone = ?", (formatted_phone,))
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"User not found: {formatted_phone}")
            return None

        user_id, password_hash, name, city, role = user_data
        
        if not verify_password(password, password_hash):
            print(f"Password verification failed for: {formatted_phone}")
            return None

        token = create_access_token({"sub": formatted_phone})
        print(f"Login successful for: {formatted_phone}")
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user_id,
                "phone": formatted_phone,
                "name": name,
                "city": city,
                "role": role,
                "avatar": None
            }
        }

def reset_password(phone: str, new_password: str) -> dict:
    print(f"Resetting password for phone: {phone}")
    formatted_phone = format_russian_phone(phone)
    print(f"Formatted phone for reset: {formatted_phone}")

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Ищем пользователя в базе данных
        cursor.execute("SELECT id FROM users WHERE phone = ?", (formatted_phone,))
        if not cursor.fetchone():
            print(f"User not found for password reset: {formatted_phone}")
            raise ValueError("User not found")

        # Обновляем пароль
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE phone = ?
        """, (hash_password(new_password), formatted_phone))
        
        conn.commit()
        
        print(f"Password reset successfully for: {formatted_phone}")
        return {"success": True, "message": "Password reset successfully"}

def get_user_by_phone(phone: str):
    """Получить пользователя по номеру телефона"""
    print(f"Getting user by phone: {phone}")
    formatted_phone = format_russian_phone(phone)
    print(f"Formatted phone: {formatted_phone}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, phone, name, city, role FROM users WHERE phone = ?", (formatted_phone,))
        user_data = cursor.fetchone()
        print(f"Database result: {user_data}")
        
        if user_data:
            user_dict = {
                'id': user_data[0],
                'phone': user_data[1],
                'name': user_data[2],
                'city': user_data[3],
                'role': user_data[4]
            }
            print(f"Returning user: {user_dict}")
            return user_dict
        print("No user found")
        return None

def update_user_profile(user_id: int, **kwargs) -> dict:
    """Обновить профиль пользователя"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что пользователь существует
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError("User not found")
        
        # Формируем SQL для обновления
        update_fields = []
        values = []
        
        for key, value in kwargs.items():
            if value is not None and key in ['name', 'surname', 'patronymic', 'email', 'city']:
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        if not update_fields:
            return {"success": True, "message": "No fields to update"}
        
        # Добавляем updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        # Выполняем обновление
        sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        
        return {"success": True, "message": "Profile updated successfully"}

def get_current_user_from_token(token: str):
    """Получить пользователя из JWT токена"""
    try:
        print(f"Decoding token: {token[:20]}...")
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Token payload: {payload}")
        phone = payload.get("sub")
        print(f"Extracted phone: {phone}")
        
        if phone is None:
            print("No phone in token payload")
            return None
            
        # Получаем пользователя по номеру телефона
        user = get_user_by_phone(phone)
        print(f"User from phone: {user}")
        return user
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.JWTError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def update_user_profile(user_id: int, profile_data: dict) -> dict:
    """Обновляет профиль пользователя в базе данных"""
    try:
        print(f"Updating profile for user {user_id} with data: {profile_data}")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Получаем текущие данные пользователя
            cursor.execute("SELECT phone, name, city FROM users WHERE id = ?", (user_id,))
            current_user = cursor.fetchone()
            
            if not current_user:
                raise ValueError("User not found")
            
            current_phone, current_name, current_city = current_user
            
            # Обновляем только переданные поля
            new_name = current_name
            new_city = current_city
            
            # Формируем новое имя из first_name и last_name
            if profile_data.get('first_name') or profile_data.get('last_name'):
                first_name = profile_data.get('first_name', '')
                last_name = profile_data.get('last_name', '')
                new_name = f"{first_name} {last_name}".strip()
            
            if profile_data.get('city'):
                new_city = profile_data['city']
            
            # Обновляем в базе данных
            cursor.execute("""
                UPDATE users 
                SET name = ?, city = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_name, new_city, user_id))
            
            conn.commit()
            
            print(f"Profile updated successfully for user {user_id}")
            
            # Возвращаем обновленные данные
            return {
                'id': user_id,
                'phone': current_phone,
                'name': new_name,
                'city': new_city,
                'first_name': profile_data.get('first_name', ''),
                'last_name': profile_data.get('last_name', ''),
                'email': profile_data.get('email', '')
            }
            
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        raise e

def change_user_password(user_id: int, current_password: str, new_password: str) -> bool:
    """Изменяет пароль пользователя"""
    try:
        print(f"Changing password for user {user_id}")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Получаем текущий хешированный пароль
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError("User not found")
            
            current_hashed = result[0]
            
            # Проверяем текущий пароль
            if not verify_password(current_password, current_hashed):
                raise ValueError("Current password is incorrect")
            
            # Хешируем новый пароль
            new_hashed = hash_password(new_password)
            
            # Обновляем пароль в базе данных
            cursor.execute("""
                UPDATE users 
                SET password = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_hashed, user_id))
            
            conn.commit()
            
            print(f"Password changed successfully for user {user_id}")
            return True
            
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        raise e

def get_user_profile(user_id: int) -> dict:
    """Получает полный профиль пользователя"""
    try:
        print(f"Getting profile for user {user_id}")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, phone, name, city, role FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError("User not found")
            
            user_id, phone, name, city, role = result
            
            # Разделяем имя на first_name и last_name
            name_parts = name.split(' ', 1) if name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            profile = {
                'id': user_id,
                'phone': phone,
                'name': name,
                'city': city,
                'role': role,
                'first_name': first_name,
                'last_name': last_name,
                'email': ''  # Email пока не хранится в БД
            }
            
            print(f"Profile retrieved: {profile}")
            return profile
            
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        raise e