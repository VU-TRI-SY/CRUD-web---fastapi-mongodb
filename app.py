from fastapi import FastAPI, Query, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio
from pymongo import MongoClient

app = FastAPI(
    title="Production Collection API",
)

MONGODB_URL = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.book_collection
book_collection = db.get_collection("books")

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class BookModel(BaseModel):
    id : Annotated[str | None, Field(alias='_id')] = None,
    title : Annotated[str | None, Field()] = None,
    isbn : Annotated[str | None, Field()] = None,
    categories : Annotated[list[str] | None, Field()] = None,
    # title: str | None = Field(...),
    # isbn : str | None = Field(...),
    # categories : list[str] | None = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title" : "Unlocking Android", 
                "isbn" : "1933988673", 
                "categories" : [ "Open Source", "Mobile" ] 
            }
        },
    )

@app.get('/books/')
async def list_books(
    id : str | None = None,
    title: str | None = None,
    isbn : str | None = None,
    categories : str | None = None
    ):

    query = {}

    if id:
        query['_id'] = ObjectId(id)

    if title:
        query['title'] = title
    
    if isbn: 
        query['isbn'] = isbn

    if categories:
        query['categories'] = categories

    books = await book_collection.find(query).to_list(1000)

    for b in books:
        b['_id'] = str(b['_id'])

    return books

@app.post(
    "/books/",
    response_description="Add new book",
    response_model=BookModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=True,
)

async def create_book(book : BookModel = Body(...)):
    new_book = await book_collection.insert_one(
        book.model_dump(by_alias=True, exclude='_id')
    )

    created_book = await book_collection.find_one(
        {"_id": new_book.inserted_id}
    )

    created_book['_id'] = str(created_book['_id'])

    return created_book

@app.put(
    '/books/{id}',
    response_description="Update a book",
    response_model=BookModel,
)

async def update_book(id:str, new_book: BookModel = Body(...)):
    query = { k: v for k, v in new_book.model_dump(by_alias=True, exclude='_id').items() if v is not None and v[0] is not None }

    if len(query) < 1:
        return False
    
    book = await book_collection.find_one({"_id": ObjectId(id)})

    if book:
        updated_result = await book_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": query}
        )

        if updated_result:
            updated_book = await book_collection.find_one(
                {"_id": ObjectId(id)}
            )

            updated_book['_id'] = str(updated_book['_id'])
            return updated_book
        else:
            raise HTTPException(status_code=404, detail=f"Book {id} not found")

@app.delete("/books/{id}", response_description="Delete a book")

async def delete_book(id : str):

    delete_result = await book_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Book {id} not found")

