from datetime import date, timedelta, time
from decimal import Decimal

from app.database import Base, engine, SessionLocal
from app.models import User, Movie, Theatre, Show
from app.security import hash_password


Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # 1. Create the admin account
    admin = db.query(User).filter(
        User.email == "admin@cinehub.local"
    ).first()

    if not admin:
        admin = User(
            name="CineHub Admin",
            email="admin@cinehub.local",
            hashed_password=hash_password("Admin123!"),
            is_admin=True
        )
        db.add(admin)

    # 2. Add Christopher Nolan movies
    if db.query(Movie).count() == 0:
        movies = [
            Movie(
                title="Inception",
                description=(
                    "A skilled thief enters people's dreams to steal secrets. "
                    "He receives a challenging mission to plant an idea "
                    "inside someone's mind."
                ),
                genre="Sci-Fi",
                language="English",
                duration_minutes=148,
                release_date=date(2010, 7, 16),
                poster_url=(
                    "https://image.tmdb.org/t/p/w500/"
                    "oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"
                ),
                rating=Decimal("8.8")
            ),

            Movie(
                title="Interstellar",
                description=(
                    "A team of astronauts travels through a wormhole "
                    "in search of a new home for humanity."
                ),
                genre="Sci-Fi",
                language="English",
                duration_minutes=169,
                release_date=date(2014, 11, 7),
                poster_url=(
                    "https://image.tmdb.org/t/p/w500/"
                    "gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
                ),
                rating=Decimal("8.7")
            ),

            Movie(
                title="The Dark Knight",
                description=(
                    "Batman faces the Joker, a criminal mastermind "
                    "who brings chaos to Gotham City."
                ),
                genre="Action",
                language="English",
                duration_minutes=152,
                release_date=date(2008, 7, 18),
                poster_url=(
                    "https://image.tmdb.org/t/p/w500/"
                    "qJ2tW6WMUDux911r6m7haRef0WH.jpg"
                ),
                rating=Decimal("9.0")
            ),

            Movie(
                title="Oppenheimer",
                description=(
                    "Scientist J. Robert Oppenheimer leads the "
                    "Manhattan Project and faces the consequences "
                    "of developing the atomic bomb."
                ),
                genre="Biography",
                language="English",
                duration_minutes=180,
                release_date=date(2023, 7, 21),
                poster_url=(
                    "https://image.tmdb.org/t/p/w500/"
                    "ptpr0kGAckfQkJeJIt8st5dglvd.jpg"
                ),
                rating=Decimal("8.3")
            ),

            Movie(
                title="Tenet",
                description=(
                    "A secret agent investigates a dangerous technology "
                    "that manipulates the flow of time."
                ),
                genre="Sci-Fi",
                language="English",
                duration_minutes=150,
                release_date=date(2020, 9, 3),
                poster_url=(
                    "https://image.tmdb.org/t/p/w500/"
                    "k68nPLbIST6NP96JmTxmZijEvCA.jpg"
                ),
                rating=Decimal("7.3")
            ),

            Movie(
                title="Dunkirk",
                description=(
                    "Allied soldiers struggle to survive and escape "
                    "during the evacuation of Dunkirk in World War II."
                ),
                genre="War",
                language="English",
                duration_minutes=107,
                release_date=date(2017, 7, 21),
                poster_url=(
                    "https://image.tmdb.org/t/p/w500/"
                    "b4Oe15CGLL61PEcMM8A9y1X2o0r.jpg"
                ),
                rating=Decimal("7.8")
            ),
        ]

        db.add_all(movies)

    # 3. Add theatres
    if db.query(Theatre).count() == 0:
        theatres = [
            Theatre(
                name="PVR Orion",
                city="Bengaluru",
                address="Rajajinagar, Bengaluru",
                total_seats=40
            ),
            Theatre(
                name="Cinepolis Central",
                city="Bengaluru",
                address="MG Road, Bengaluru",
                total_seats=40
            ),
            Theatre(
                name="Galaxy Multiplex",
                city="Mysuru",
                address="VV Mohalla, Mysuru",
                total_seats=40
            ),
        ]

        db.add_all(theatres)

    # Save movies and theatres before creating shows
    db.commit()

    movies = db.query(Movie).all()
    theatres = db.query(Theatre).all()

    # 4. Create showtimes
    if db.query(Show).count() == 0:
        today = date.today()

        show_times = [
            time(10, 0),
            time(13, 30),
            time(17, 0),
            time(20, 30)
        ]

        shows = []

        for movie in movies:
            for theatre in theatres:
                for offset, show_time in enumerate(show_times[:2]):
                    shows.append(
                        Show(
                            movie_id=movie.id,
                            theatre_id=theatre.id,
                            show_date=today + timedelta(days=offset),
                            show_time=show_time,
                            price=(
                                Decimal("180.00")
                                + Decimal(offset * 40)
                            )
                        )
                    )

        db.add_all(shows)

    db.commit()

    print("CineHub database seeding completed!")
    print("Movies: Christopher Nolan collection")
    print("Admin login: admin@cinehub.local / Admin123!")

finally:
    db.close()