from fastapi import APIRouter, HTTPException, Header
from app.auth.models import PhoneRequest, SMSRequest, PasswordRequest, LoginRequest, AuthResponse, ProfileUpdateRequest, PasswordChangeRequest
from app.auth.service import register_user, authenticate_user, reset_password, verify_sms_code, generate_sms_code, update_user_profile, change_user_password, get_user_profile, get_current_user_from_token

router = APIRouter()

@router.post("/request-code", response_model=AuthResponse)
async def request_sms_code(request: PhoneRequest):
    try:
        print(f"Requesting SMS code for phone: {request.phone}")
        code = generate_sms_code(request.phone)
        print(f"SMS code generated: {code}")
        return AuthResponse(success=True, message="SMS code sent successfully")
    except Exception as e:
        print(f"Error requesting SMS code: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-code", response_model=AuthResponse)
async def verify_sms_code_endpoint(request: SMSRequest):
    print(f"Verifying SMS code for phone: {request.phone}, code: {request.code}")
    if verify_sms_code(request.phone, request.code):
        print(f"SMS code verified successfully for: {request.phone}")
        return AuthResponse(success=True, message="Code verified successfully")
    else:
        print(f"Invalid SMS code for: {request.phone}")
        raise HTTPException(status_code=400, detail="Invalid SMS code")

@router.post("/register", response_model=AuthResponse)
async def register(request: PasswordRequest):
    try:
        print(f"Registering user with phone: {request.phone}, name: {request.name}, city: {request.city}")
        result = register_user(request.phone, request.password, request.name, request.city)
        print(f"Registration result: {result}")
        return AuthResponse(**result)
    except ValueError as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        print(f"Login attempt for phone: {request.phone}")
        result = authenticate_user(request.phone, request.password)
        print(f"Authentication result: {result}")
        if result:
            print(f"Returning successful response with token: {result.get('token', 'No token')[:20] if result.get('token') else 'No token'}...")
            return AuthResponse(**result)
        else:
            print("Authentication failed - no result returned")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password", response_model=AuthResponse)
async def reset_password_endpoint(request: PasswordRequest):
    try:
        print(f"Resetting password for phone: {request.phone}")
        result = reset_password(request.phone, request.password)
        print(f"Password reset result: {result}")
        return AuthResponse(**result)
    except ValueError as e:
        print(f"Password reset error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile", response_model=dict)
async def get_profile(authorization: str = Header(None)):
    """Получить профиль текущего пользователя"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        profile = get_user_profile(user_id)
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=dict)
async def update_profile(
    profile_data: ProfileUpdateRequest, 
    authorization: str = Header(None)
):
    """Обновить профиль пользователя"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        
        # Преобразуем Pydantic модель в словарь
        profile_dict = profile_data.model_dump(exclude_unset=True)
        
        # Обновляем профиль
        updated_profile = update_user_profile(user_id, profile_dict)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": updated_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/change-password", response_model=AuthResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    authorization: str = Header(None)
):
    """Изменить пароль пользователя"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        
        # Изменяем пароль
        change_user_password(user_id, password_data.current_password, password_data.new_password)
        
        return AuthResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
