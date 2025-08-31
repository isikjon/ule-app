from fastapi import APIRouter, HTTPException
from app.auth.models import PhoneRequest, SMSRequest, PasswordRequest, LoginRequest, AuthResponse
from app.auth.service import register_user, authenticate_user, reset_password, verify_sms_code, generate_sms_code

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
        if result:
            return AuthResponse(**result)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        print(f"Login error: {str(e)}")
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
