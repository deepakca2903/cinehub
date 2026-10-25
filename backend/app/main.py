import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, movies, discovery, bookings, admin
from . import models  # register ORM models before create_all

load_dotenv()
app = FastAPI(title="CineHub API", version="1.0.0", description="Smart Movie Ticket Booking API")

origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to CineHub API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(discovery.router)
app.include_router(bookings.router)
app.include_router(admin.router)
