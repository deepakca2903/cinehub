from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Movie
from ..schemas import MovieOut

router = APIRouter(prefix="/api/movies", tags=["Movies"])

@router.get("", response_model=list[MovieOut])
def list_movies(search: str | None = Query(default=None, max_length=100), db: Session = Depends(get_db)):
    query = db.query(Movie)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(or_(Movie.title.ilike(pattern), Movie.genre.ilike(pattern), Movie.language.ilike(pattern)))
    return query.order_by(Movie.title.asc()).all()

@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    return movie
