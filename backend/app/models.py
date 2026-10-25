from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, Time, ForeignKey, Text,
    UniqueConstraint, CheckConstraint, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    bookings = relationship("Booking", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    genre: Mapped[str] = mapped_column(String(100), default="Drama", nullable=False)
    language: Mapped[str] = mapped_column(String(80), default="English", nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    release_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    poster_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(3, 1), default=0, nullable=False)
    shows = relationship("Show", back_populates="movie")
    __table_args__ = (CheckConstraint("duration_minutes > 0", name="ck_movie_duration_positive"),)

class Theatre(Base):
    __tablename__ = "theatres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
    shows = relationship("Show", back_populates="theatre")

class Show(Base):
    __tablename__ = "shows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    theatre_id: Mapped[int] = mapped_column(ForeignKey("theatres.id", ondelete="CASCADE"), nullable=False)
    show_date: Mapped[Date] = mapped_column(Date, nullable=False)
    show_time: Mapped[Time] = mapped_column(Time, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    movie = relationship("Movie", back_populates="shows")
    theatre = relationship("Theatre", back_populates="shows")
    bookings = relationship("Booking", back_populates="show")
    __table_args__ = (CheckConstraint("price >= 0", name="ck_show_price_nonnegative"),)

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="CONFIRMED", nullable=False)
    booking_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    user = relationship("User", back_populates="bookings")
    show = relationship("Show", back_populates="bookings")
    __table_args__ = (
        UniqueConstraint("show_id", "seat_number", name="uq_show_seat"),
        CheckConstraint("status IN ('CONFIRMED', 'CANCELLED')", name="ck_booking_status"),
    )
