from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.core.security import create_access_token, verify_password



def register_user(db: Session, email: str, password: str) -> User:
    # 1. look for an existing user with this email
    
    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    # 2. if found: raise HTTPException(status_code=409, detail="Email already registered")
    if existing:
        raise HTTPException(status_code=409 , detail="Email already registered")

    new_user = User(email=email, password_hash=hash_password(password))
    
    # 3. create User(email=..., password_hash=hash_password(password))
    # 4. db.add(user), db.commit(), db.refresh(user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # 5. return user
    return new_user

def authenticate_user(db:Session , email:str , password:str) -> str:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(user_id=user.id, role=user.role)
    return access_token