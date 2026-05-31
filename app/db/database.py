"""
SQLAlchemy setup: engine, session factory, Base, and ORM models.
"""
from sqlalchemy import Column, Integer, String, Text, create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

from app.core.config import SQLALCHEMY_DATABASE_URL

# ── Engine & session ─────────────────────────────────────────────────────────
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only; harmless for Postgres
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── ORM model ────────────────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, index=True, nullable=False)
    product_name = Column(String,  nullable=False)
    status       = Column(String,  default="Pending")
    details      = Column(Text)


# ── FastAPI dependency ────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)
