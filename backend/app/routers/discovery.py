from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import Theatre, Show, Booking
from ..schemas import TheatreOut, ShowOut

router = APIRouter(prefix="/api", tags=["Theatres and Shows"])

@router.get("/theatres", response_model=list[TheatreOut])
def list_theatres(city: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Theatre)
    if city:
        query = query.filter(Theatre.city.ilike(f"%{city.strip()}%"))
    return query.order_by(Theatre.city, Theatre.name).all()

@router.get("/shows", response_model=list[ShowOut])
def list_shows(movie_id: int | None = None, city: str | None = None, db: Session = Depends(get_db)):
    from ..models import Movie
    query = db.query(Show, Movie, Theatre).join(Movie, Show.movie_id == Movie.id).join(Theatre, Show.theatre_id == Theatre.id)
    if movie_id:
        query = query.filter(Show.movie_id == movie_id)
    if city:
        query = query.filter(Theatre.city.ilike(f"%{city.strip()}%"))
    rows = query.order_by(Show.show_date, Show.show_time).all()
    return [
        ShowOut(id=s.id, movie_id=s.movie_id, theatre_id=s.theatre_id, show_date=s.show_date,
                show_time=s.show_time, price=s.price, movie_title=m.title,
                theatre_name=t.name, city=t.city)
        for s, m, t in rows
    ]

@router.get("/shows/{show_id}/seats")
def show_seats(show_id: int, db: Session = Depends(get_db)):
    show = db.get(Show, show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found.")
    booked = db.query(Booking.seat_number).filter(
        Booking.show_id == show_id, Booking.status == "CONFIRMED"
    ).all()
    booked_set = {row[0] for row in booked}
    total = show.theatre.total_seats
    rows = (total + 7) // 8
    seats = []
    for idx in range(total):
        row = idx // 8
        col = idx % 8
        seat = f"{chr(65 + row)}{col + 1}"
        seats.append({"seat_number": seat, "status": "BOOKED" if seat in booked_set else "AVAILABLE"})
    return {"show_id": show_id, "price": show.price, "seats": seats}
