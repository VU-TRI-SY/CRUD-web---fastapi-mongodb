from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float

from .database import Base

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    published_date = Column(Date, nullable=True)
    isbn = Column(String, unique=True, nullable=False)
    pages = Column(Integer, nullable=False)
    cover = Column(String, nullable=True)  
    language = Column(String, nullable=False)
    price = Column(Float, nullable=False)