from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.models import user, ride, booking  # noqa: F401
from app.routers import auth, users, rides, bookings

app = FastAPI(title="Rideshare API", version="0.1.0")

# Create tables (MVP). For prod, use Alembic migrations.
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"ok": True}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rides.router)
app.include_router(bookings.router)
