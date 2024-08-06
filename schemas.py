from pydantic import BaseModel
from datetime import date, datetime, time, timedelta

class Book(BaseModel):
    id : int | None = None
    title : str | None = None
    author : str | None = None
    published_date : date | None = None
    isbn : str | None = None
    pages : int | None = None
    cover : str | None = None
    language : str | None = None
    price : float | None = None