from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(80), default="Community Contributor")
    wheelchair: Mapped[bool] = mapped_column(Boolean, default=True)
    no_stairs: Mapped[bool] = mapped_column(Boolean, default=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")

class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    address: Mapped[str] = mapped_column(String(240))
    type: Mapped[str] = mapped_column(String(80))
    icon: Mapped[str] = mapped_column(String(10), default="📍")
    verified: Mapped[str] = mapped_column(String(80))
    map_x: Mapped[float] = mapped_column(Float, default=50)
    map_y: Mapped[float] = mapped_column(Float, default=50)
    tags: Mapped[str] = mapped_column(Text, default="")
    accessibility: Mapped[list["AccessibilityCheck"]] = relationship(
        back_populates="venue", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="venue", cascade="all, delete-orphan"
    )
    saved_by: Mapped[list["SavedPlace"]] = relationship(
        back_populates="venue", cascade="all, delete-orphan"
    )

class AccessibilityCheck(Base):
    __tablename__ = "accessibility_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(240))
    percent: Mapped[int] = mapped_column(Integer)
    venue: Mapped["Venue"] = relationship(back_populates="accessibility")

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    venue: Mapped["Venue"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")

class SavedPlace(Base):
    __tablename__ = "saved_places"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    venue: Mapped["Venue"] = relationship(back_populates="saved_by")
