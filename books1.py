from typing import Optional
from fastapi import FastAPI
from enum import Enum

app = FastAPI()

BOOKS = {
    'book-1': {'title': 'Title-1', 'Author':'Author-1'},
    'book-2': {'title': 'Title-2', 'Author':'Author-2'},
    'book-3': {'title': 'Title-3', 'Author':'Author-3'},
    'book-4': {'title': 'Title-4', 'Author':'Author-4'},
    'book-5': {'title': 'Title-5', 'Author':'Author-5'}
}


# class DirectionName(str, Enum):
#     north = "North"
#     south = "South"
#     west = "West"
#     east = "East"

# @app.get("/")
# async def read_all_books(skip_this_book: Optional[str] = None):
#     if skip_this_book:
#         new_books = BOOKS.copy()
#         del new_books[skip_this_book]
#         return new_books
#     return BOOKS
# # async def first_api():
# #     return {"Message" : "Hello Vineetha"}

''' Also query parameter'''


@app.get("/assignment/")
async def read_new(read_book : str):
    if read_book in BOOKS:
        return BOOKS[read_book]


@app.get("/{book_name}")
async def book_details(book_name: str):
    return BOOKS[book_name]

# @app.get("/direction/{direction_name}")
# async def get_direction(direction_name : DirectionName):
#     if direction_name == DirectionName.north:
#         return {"Direction": direction_name, "Position": "Up"}
#     if direction_name == DirectionName.south:
#         return {"Direction": direction_name, "Position": "Down"}
#     if direction_name == DirectionName.west:
#         return {"Direction": direction_name, "Position": "Left"}
#     return {"Direction": direction_name , "Position": "Right"}

# @app.get("/books/{book_id}")
# async def read_book_id(book_id : int):
#    return{"book id": book_id}


@app.post("/")
async def create_book(book_title, book_author):
    current_id = 0
    if len(BOOKS)>0:
        for book in BOOKS:
            x=int(book.split('-')[-1])
            if x>current_id :
                current_id=x
    BOOKS[f'book-{current_id+1} '] = {'title': book_title, 'Author': book_author}
    return BOOKS[f'book-{current_id+1} ']


@app.put("/{book_name}")
async def update_book(book_name: str, book_title: str, book_author: str):
    new_info = {"title": book_title, "Author": book_author}
    BOOKS[book_name] = new_info
    return new_info


# @app.delete("/{book_name}")
# async def delete_book(book_name: str):
#     if book_name in BOOKS:
#         del BOOKS[book_name]
#     return f'Book-{book_name} is deleted'


@app.delete("/Assignment")
async def delete_book(book_name: str = "book-3"):
    if book_name in BOOKS:
        del BOOKS[book_name]
    return f'Book-{book_name} is deleted'