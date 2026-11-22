from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import User
from backend.core.security import create_access_token, verify_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Authentication & Security"])

class LoginRequest(BaseModel):
    phone: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    phone: str
    role: str
    department_id: Optional[str] = None

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    clean_phone = payload.phone.strip()
    user = db.query(User).filter(User.phone == clean_phone).first()

    if not user:
        # For prototype convenience, if an unseeded user logs in with phone, register as CITIZEN
        user = User(phone=clean_phone, name="Citizen", role="CITIZEN")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user_id=user.id, role=user.role)
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        name=user.name or "User",
        phone=user.phone,
        role=user.role,
        department_id=user.department_id
    )

@router.get("/me")
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    token = authorization.split(" ")[1]
    token_data = verify_access_token(token)

    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    return {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "department_id": user.department_id
    }
