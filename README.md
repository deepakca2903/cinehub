# CineHub — Smart Movie Ticket Booking System

Stack: React + Vite + Axios + FastAPI + SQLAlchemy + MySQL.

## Features in this starter
- Register/login with JWT and hashed passwords
- Browse movies and view movie details
- Browse theatres and showtimes
- View seats and book multiple seats in a single database transaction
- Prevent duplicate seat bookings
- View/cancel your bookings
- Admin-only CRUD endpoints for movies, theatres, and shows
- Seed demo data

> Payments are simulated. Do not use this starter as-is for real-money payments or production deployment.

## 1. Requirements
- Python 3.11+
- Node.js 20+
- MySQL 8+
- Git (optional)

## 2. Create database
Open MySQL Workbench or MySQL command line and run:

```sql
CREATE DATABASE cinehub_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 3. Backend setup (Windows PowerShell)
Open a terminal in `backend`:

```powershell
py -m venv myenv
.\myenv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`. Set `DATABASE_URL` with your own MySQL username/password:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/cinehub_db
SECRET_KEY=replace-this-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_ORIGIN=http://localhost:5173
```
If your MySQL root user has no password (not recommended), leave the password section empty, e.g. `mysql+pymysql://root:@127.0.0.1:3306/cinehub_db`.

Start the backend:
```powershell
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs` to explore the API.

## 4. Seed demo data
In a second terminal, activate the same virtual environment and run:
```powershell
python seed.py
```
Demo admin login:
- Email: `admin@cinehub.local`
- Password: `Admin123!`

Change this password and secret before any deployment. Seed data is only for local development.

## 5. Frontend setup
Open a new terminal in `frontend`:
```powershell
npm install
Copy-Item .env.example .env
npm run dev
```
Open the URL printed by Vite, usually `http://localhost:5173`.

## 6. Run order
1. Start MySQL.
2. Start FastAPI in `backend`.
3. Run `python seed.py` once.
4. Start React in `frontend`.

## API overview
- `POST /api/auth/register`
- `POST /api/auth/login` (OAuth2 form, `username` field is the email)
- `GET /api/movies`
- `GET /api/movies/{movie_id}`
- `GET /api/theatres`
- `GET /api/shows?movie_id=1&city=Bengaluru`
- `GET /api/shows/{show_id}/seats`
- `POST /api/bookings`
- `GET /api/bookings/me`
- `POST /api/bookings/{booking_id}/cancel`
- Admin endpoints under `/api/admin/*`

## Important implementation notes
- Booking requests lock the selected show row and verify every requested seat is still available before inserting bookings.
- A database unique constraint prevents the same seat from being booked twice for the same show.
- In production, also configure HTTPS, secure secrets, rate limiting, migrations (Alembic), logging, backups, payment-provider webhooks, and a proper seat-hold/expiry workflow.
