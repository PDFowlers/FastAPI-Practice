from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi', user = 'postgres', password = '', cursor_factory= RealDictCursor)
        cursor = conn.cursor()
        print('Database connection successfull')
        break
    except:
        print('Connection Failed')
        print("Error: ")
        time.sleep(2)

# "/" refers to the root directory. You can change the desired url by writting more of a "url" after "/"
@app.get("/")
def root():
    return {"message": "Welcome to my API"}

@app.get('/posts', response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all() # .query is essentially using the "SELECT" SQL command
    return posts

@app.get('/posts/{id}', response_model=schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first() # '.filter' command functions similar to WHERE in sql '.first' will return the first instance of the desired filter
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return post

@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict()) # '**' will unpack the dictionary for me so that you dont need to actually type out each field of the model(table) individually
    db.add(new_post)
    db.commit() #add + commit function to actually insert the new post into the table
    db.refresh(new_post) #This is similar to the 'RETURNING' function in SQL language
    return new_post

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if not deleted_post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: schemas.PostBase, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
