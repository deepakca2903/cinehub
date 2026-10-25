from datetime import date, time, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    is_admin: bool

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class MovieIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    genre: str = "Drama"
    language: str = "English"
    duration_minutes: int = Field(gt=0)
    release_date: date | None = None
    poster_url: str = ""
    rating: Decimal = Field(default=Decimal("0.0"), ge=0, le=10)

class MovieOut(MovieIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class TheatreIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    address: str = ""
    total_seats: int = Field(default=40, ge=1, le=500)

class TheatreOut(TheatreIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ShowIn(BaseModel):
    movie_id: int
    theatre_id: int
    show_date: date
    show_time: time
    price: Decimal = Field(ge=0)

class ShowOut(BaseModel):
    id: int
    movie_id: int
    theatre_id: int
    show_date: date
    show_time: time
    price: Decimal
    movie_title: str
    theatre_name: str
    city: str

class BookingIn(BaseModel):
    show_id: int
    seats: list[str] = Field(min_length=1, max_length=10)

    @field_validator("seats")
    @classmethod
    def validate_seats(cls, value):
        clean = [s.strip().upper() for s in value]
        if len(clean) != len(set(clean)):
            raise ValueError("Duplicate seats were provided.")
        for seat in clean:
            if len(seat) < 2 or len(seat) > 4 or not seat[0].isalpha() or not seat[1:].isdigit():
                raise ValueError(f"Invalid seat format: {seat}")
        return clean

class BookingOut(BaseModel):
    id: int
    show_id: int
    seat_number: str
    status: str
    booking_time: datetime
    amount: Decimal
    movie_title: str
    theatre_name: str
    city: str
    show_date: date
    show_time: time
