from fastapi import Depends, FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.routers import admin, auth, categories, orders, products
from app.schemas.user import UserOut

app = FastAPI(title="E-commerce API")

from app.core.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}


@app.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user
