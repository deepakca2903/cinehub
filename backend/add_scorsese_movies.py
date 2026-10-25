from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models import Movie


scorsese_movies = [
    {
        "title": "Goodfellas",
        "description": "The rise and fall of a young man in the world of organized crime.",
        "genre": "Crime",
        "language": "English",
        "duration_minutes": 145,
        "release_date": date(1990, 9, 19),
        "poster_url": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
        "rating": Decimal("8.7"),
    },
    {
        "title": "The Wolf of Wall Street",
        "description": "The story of stockbroker Jordan Belfort and his rise and fall in the financial world.",
        "genre": "Biography",
        "language": "English",
        "duration_minutes": 180,
        "release_date": date(2013, 12, 25),
        "poster_url": "https://image.tmdb.org/t/p/w500/34m2tygAYBGqA9MXKhRDtzYd4MR.jpg",
        "rating": Decimal("8.2"),
    },
    {
        "title": "Shutter Island",
        "description": "Two investigators visit a remote hospital for the criminally insane to investigate a disappearance.",
        "genre": "Thriller",
        "language": "English",
        "duration_minutes": 138,
        "release_date": date(2010, 2, 19),
        "poster_url": "https://image.tmdb.org/t/p/w500/4GDy0PHYX3VRXUtwK5ysFbg3kEx.jpg",
        "rating": Decimal("8.2"),
    },
    {
        "title": "The Departed",
        "description": "An undercover police officer and a criminal informant attempt to expose each other.",
        "genre": "Crime",
        "language": "English",
        "duration_minutes": 151,
        "release_date": date(2006, 10, 6),
        "poster_url": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg",
        "rating": Decimal("8.5"),
    },
    {
        "title": "Taxi Driver",
        "description": "A troubled New York taxi driver becomes increasingly alienated from society.",
        "genre": "Drama",
        "language": "English",
        "duration_minutes": 114,
        "release_date": date(1976, 2, 8),
        "poster_url": "https://image.tmdb.org/t/p/w500/ekstpH614fwDX8DUln1a2Opz0N8.jpg",
        "rating": Decimal("8.2"),
    },
    {
        "title": "Killers of the Flower Moon",
        "description": "A series of murders targets members of the Osage Nation in 1920s Oklahoma.",
        "genre": "Crime",
        "language": "English",
        "duration_minutes": 206,
        "release_date": date(2023, 10, 20),
        "poster_url": "https://image.tmdb.org/t/p/w500/dB6Krk806zeqd0YNp2ngQ9zXteH.jpg",
        "rating": Decimal("7.6"),
    },
]


db = SessionLocal()

try:
    existing_titles = {
        title.lower()
        for (title,) in db.query(Movie.title).all()
    }

    added = 0

    for movie_data in scorsese_movies:
        if movie_data["title"].lower() in existing_titles:
            print(f"Already exists: {movie_data['title']}")
            continue

        db.add(Movie(**movie_data))
        existing_titles.add(movie_data["title"].lower())
        added += 1

    db.commit()
    print(f"\nSuccessfully added {added} Martin Scorsese movies!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()