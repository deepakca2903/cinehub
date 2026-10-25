from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models import Movie


nolan_movies = [
    {
        "title": "Inception",
        "description": "A skilled thief enters people's dreams to plant an idea.",
        "genre": "Sci-Fi",
        "language": "English",
        "duration_minutes": 148,
        "release_date": date(2010, 7, 16),
        "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "rating": Decimal("8.8"),
    },
    {
        "title": "Interstellar",
        "description": "Astronauts travel through a wormhole to search for a new home for humanity.",
        "genre": "Sci-Fi",
        "language": "English",
        "duration_minutes": 169,
        "release_date": date(2014, 11, 7),
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "rating": Decimal("8.7"),
    },
    {
        "title": "The Dark Knight",
        "description": "Batman faces the Joker, a criminal mastermind bringing chaos to Gotham City.",
        "genre": "Action",
        "language": "English",
        "duration_minutes": 152,
        "release_date": date(2008, 7, 18),
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "rating": Decimal("9.0"),
    },
    {
        "title": "Oppenheimer",
        "description": "Scientist J. Robert Oppenheimer leads the Manhattan Project.",
        "genre": "Biography",
        "language": "English",
        "duration_minutes": 180,
        "release_date": date(2023, 7, 21),
        "poster_url": "https://image.tmdb.org/t/p/w500/ptpr0kGAckfQkJeJIt8st5dglvd.jpg",
        "rating": Decimal("8.3"),
    },
    {
        "title": "Tenet",
        "description": "A secret agent investigates technology that manipulates the flow of time.",
        "genre": "Sci-Fi",
        "language": "English",
        "duration_minutes": 150,
        "release_date": date(2020, 9, 3),
        "poster_url": "https://image.tmdb.org/t/p/w500/k68nPLbIST6NP96JmTxmZijEvCA.jpg",
        "rating": Decimal("7.3"),
    },
    
]


db = SessionLocal()

try:
    existing_movies = db.query(Movie).order_by(Movie.id).all()

    # Reuse existing movie records so showtimes keep their movie IDs.
    for index, movie_data in enumerate(nolan_movies):
        if index < len(existing_movies):
            movie = existing_movies[index]
            for field, value in movie_data.items():
                setattr(movie, field, value)
        else:
            movie = Movie(**movie_data)
            db.add(movie)

    # Remove surplus movies only if they have no associated shows.
    # Never delete a movie that still has showtimes.
    for movie in existing_movies[len(nolan_movies):]:
        if not movie.shows:
            db.delete(movie)
        else:
            print(
                f"Keeping extra movie ID {movie.id} because it has showtimes."
            )

    db.commit()

    print("Movie collection updated successfully!")
    print("Current movie list:")

    for movie in db.query(Movie).order_by(Movie.id).all():
        print(f"- {movie.title} (ID: {movie.id})")

except Exception:
    db.rollback()
    raise

finally:
    db.close()