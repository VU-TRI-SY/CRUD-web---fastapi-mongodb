from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import Response
from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/book/', response_model=schemas.Book | list[schemas.Book] | None)
def get_book(id : int | None = None, skip: int = 0, limit: int = 100, db : Session = Depends(get_db)):
    if id:
        return db.query(models.Book).filter(models.Book.id == id).first()
    return db.query(models.Book).offset(skip).limit(limit).all()

@app.post('/book/', response_model=schemas.Book)
def create_book(book : schemas.Book, db : Session = Depends(get_db), ):
    db_book = db.query(models.Book).filter(models.Book.id == book.id).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book already existed")

    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book

@app.put('/book/{book_id}', response_model=schemas.Book)
def update_book(book_id : int, book : schemas.Book, db : Session = Depends(get_db)):
    db_query = db.query(models.Book).filter(models.Book.id == book_id)
    db_book = db_query.first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book with id {book_id} not found")
    
    update_data = book.model_dump(exclude_unset=True)
    db_query.filter(models.Book.id == book_id).update(update_data)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete('/book/{book_id}')
def delete_book(book_id : int, db : Session = Depends(get_db)):
    db_query = db.query(models.Book).filter(models.Book.id == book_id)
    db_book = db_query.first()
    if db_book:
        db_query.delete()
        db.commit()
        return Response(status_code=204) 

    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
