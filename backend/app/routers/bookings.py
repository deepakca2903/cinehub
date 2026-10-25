from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Booking, Show, User, Movie, Theatre
from ..schemas import BookingIn, BookingOut
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

def serialize_booking(b: Booking) -> BookingOut:
    return BookingOut(
        id=b.id, show_id=b.show_id, seat_number=b.seat_number, status=b.status,
        booking_time=b.booking_time, amount=b.amount, movie_title=b.show.movie.title,
        theatre_name=b.show.theatre.name, city=b.show.theatre.city,
        show_date=b.show.show_date, show_time=b.show.show_time
    )

@router.post("", response_model=list[BookingOut], status_code=201)
def create_booking(data: BookingIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Lock the show row so concurrent booking requests for this show serialize on MySQL/InnoDB.
    show = db.query(Show).filter(Show.id == data.show_id).with_for_update().first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found.")
    if show.show_date < __import__("datetime").date.today():
        raise HTTPException(status_code=400, detail="Cannot book a show in the past.")
    total_seats = show.theatre.total_seats
    valid_seats = set()
    for idx in range(total_seats):
        valid_seats.add(f"{chr(65 + idx // 8)}{idx % 8 + 1}")
    if not set(data.seats).issubset(valid_seats):
        raise HTTPException(status_code=400, detail="One or more seats do not exist for this theatre.")
    already = db.query(Booking.seat_number).filter(
        Booking.show_id == show.id, Booking.seat_number.in_(data.seats),
        Booking.status == "CONFIRMED"
    ).all()
    if already:
        raise HTTPException(status_code=409, detail=f"These seats are already booked: {', '.join(r[0] for r in already)}")
    bookings = [
        Booking(user_id=user.id, show_id=show.id, seat_number=seat,
                status="CONFIRMED", amount=Decimal(show.price))
        for seat in data.seats
    ]
    try:
        db.add_all(bookings)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="One or more seats were just booked. Refresh and choose again.")
    for b in bookings:
        db.refresh(b)
    return [serialize_booking(b) for b in bookings]

@router.get("/me", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bookings = db.query(Booking).options(
        joinedload(Booking.show).joinedload(Show.movie),
        joinedload(Booking.show).joinedload(Show.theatre)
    ).filter(Booking.user_id == user.id).order_by(Booking.booking_time.desc()).all()
    return [serialize_booking(b) for b in bookings]

@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.query(Booking).options(
        joinedload(Booking.show).joinedload(Show.movie),
        joinedload(Booking.show).joinedload(Show.theatre)
    ).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if booking.status != "CONFIRMED":
        raise HTTPException(status_code=400, detail="This booking is already cancelled.")
    from datetime import date
    if booking.show.show_date < date.today():
        raise HTTPException(status_code=400, detail="Past show bookings cannot be cancelled.")
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return serialize_booking(booking)
