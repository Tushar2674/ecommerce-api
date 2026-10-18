from fastapi import FastAPI , Depends
from sqlalchemy import text 
from sqlalchemy.orm import Session
from app.deps import get_current_user, get_db , require_admin
from app.routers import auth
from app.schemas.user import UserOut

app = FastAPI(title="E-commerce API")

app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}

@app.get("/me",response_model=UserOut)
def me(current_user = Depends(get_current_user)):
    return current_user

@app.get("/admin")
def admin(current_user = Depends(get_current_user)):
    if Depends(require_admin(current_user)):
        return {"message": "Admin access granted", "admin":current_user.email}
    