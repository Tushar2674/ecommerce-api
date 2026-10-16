from fastapi import FastAPI , Depends
from sqlalchemy import text 
from sqlalchemy.orm import Session
from app.deps import get_db

app = FastAPI(title="E-commerce API")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}