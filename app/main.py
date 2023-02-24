from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

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


my_posts = [{'title':'title of post 1', 'content':'content of post 1', 'id':1}, {'title':'favorite foods', 'content':'I like pizza', 'id':2}]

def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post

def find_post_index(id):
    for idx, post in enumerate(my_posts):
        if post['id'] == id:
            return idx

# "/" refers to the root directory. You can change the desired url by writting more of a "url" after "/"
@app.get("/")
def root():
    return {"message": "Welcome to my API"}

@app.get('/posts')
def get_posts():
    cursor.execute('''SELECT * FROM posts ''')
    posts = cursor.fetchall()
    return {'data':posts}

@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    cursor.execute('''SELECT * FROM posts WHERE id = %s ''', (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return {'post_detail': post}

# title str, content str, published bool, rating int
@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute('''INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *''', (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()

    return {'data': new_post}

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute('''DELETE FROM posts WHERE id = %s RETURNING *''', (id,))
    deleted_post = cursor.fetchone()
    conn.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute('''UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *''', (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    return {'updated post': updated_post}
