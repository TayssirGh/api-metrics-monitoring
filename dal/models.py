from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from dal.database import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    api_key: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    api_usage: Mapped[list["APIMetrics"]] = relationship("APIMetrics", back_populates="owner")


class APIMetrics(Base):
    __tablename__ = "api_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    endpoint: Mapped[str] = mapped_column(String, index=True)
    rows_fetched: Mapped[int] = mapped_column(Integer, default=0)
    response_size: Mapped[int] = mapped_column(Integer, default=0)
    status_code: Mapped[int] = mapped_column(Integer, default=200)

    owner: Mapped["User"] = relationship("User", back_populates="api_usage")

class Product(Base):
    __tablename__ = "products"

    id: Column = Column(Integer, primary_key=True, index=True)
    name: Column = Column(String, nullable=False)
    price: Column = Column(Integer, nullable=False)
