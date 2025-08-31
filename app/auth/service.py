import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import jwt
import hashlib

users_db: Dict[str, dict] = {}
sms_codes: Dict[str, str] = {}

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

    if formatted_phone in users_db:
        print(f"User already exists: {formatted_phone}")
        raise ValueError("User already exists")

    users_db[formatted_phone] = {
        "password": hash_password(password),
        "name": name,
        "city": city,
        "avatar": None,
        "created_at": datetime.now()
    }
    print(f"User registered successfully: {formatted_phone}")
    print(f"Current users in DB: {list(users_db.keys())}")

    return {"success": True, "message": "User registered successfully"}

def authenticate_user(phone: str, password: str) -> Optional[dict]:
    print(f"Authenticating user with phone: {phone}")
    formatted_phone = format_russian_phone(phone)
    print(f"Formatted phone: {formatted_phone}")
    print(f"Users in DB: {list(users_db.keys())}")

    if formatted_phone not in users_db:
        print(f"User not found: {formatted_phone}")
        return None

    user = users_db[formatted_phone]
    if not verify_password(password, user["password"]):
        print(f"Password verification failed for: {formatted_phone}")
        return None

    token = create_access_token({"sub": formatted_phone})
    print(f"Login successful for: {formatted_phone}")
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "phone": formatted_phone,
            "name": user.get("name"),
            "city": user.get("city"),
            "avatar": user.get("avatar")
        }
    }

def reset_password(phone: str, new_password: str) -> dict:
    print(f"Resetting password for phone: {phone}")
    formatted_phone = format_russian_phone(phone)
    print(f"Formatted phone for reset: {formatted_phone}")

    if formatted_phone not in users_db:
        print(f"User not found for password reset: {formatted_phone}")
        raise ValueError("User not found")

    users_db[formatted_phone]["password"] = hash_password(new_password)
    print(f"Password reset successfully for: {formatted_phone}")
    return {"success": True, "message": "Password reset successfully"}
