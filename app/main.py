from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

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
    return {'data':my_posts}

@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return {'post_detail': post}

# title str, content str, published bool, rating int
@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0,10000000)
    my_posts.append(post_dict)
    return {'data': post_dict}

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    # my_posts.pop(my_posts.index(post))
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    post_idx = find_post_index(id)
    if post_idx == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[post_idx] = post_dict
    return {'updated post': post_dict}
