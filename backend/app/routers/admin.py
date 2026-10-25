from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Movie, Theatre, Show
from ..schemas import MovieIn, MovieOut, TheatreIn, TheatreOut, ShowIn, ShowOut
from ..dependencies import get_admin_user
from ..models import User

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_admin_user)])

@router.post("/movies", response_model=MovieOut, status_code=201)
def create_movie(data: MovieIn, db: Session = Depends(get_db)):
    movie = Movie(**data.model_dump())
    db.add(movie); db.commit(); db.refresh(movie)
    return movie

@router.put("/movies/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, data: MovieIn, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if not movie: raise HTTPException(status_code=404, detail="Movie not found.")
    for key, value in data.model_dump().items(): setattr(movie, key, value)
    db.commit(); db.refresh(movie)
    return movie

@router.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if not movie: raise HTTPException(status_code=404, detail="Movie not found.")
    db.delete(movie); db.commit()
    return {"message": "Movie deleted."}

@router.post("/theatres", response_model=TheatreOut, status_code=201)
def create_theatre(data: TheatreIn, db: Session = Depends(get_db)):
    theatre = Theatre(**data.model_dump())
    db.add(theatre); db.commit(); db.refresh(theatre)
    return theatre

@router.post("/shows", status_code=201)
def create_show(data: ShowIn, db: Session = Depends(get_db)):
    if not db.get(Movie, data.movie_id): raise HTTPException(status_code=404, detail="Movie not found.")
    if not db.get(Theatre, data.theatre_id): raise HTTPException(status_code=404, detail="Theatre not found.")
    show = Show(**data.model_dump())
    db.add(show); db.commit(); db.refresh(show)
    return {"message": "Show created.", "show_id": show.id}
