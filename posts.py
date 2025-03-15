from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from schemas import PostCreate, PostResponse
from data_base import get_db
from models import User, Posts
import datetime

router = APIRouter()


def get_user(token: str, db: Session):
    user = db.query(User).filter(User.token == token).first()
    if datetime.datetime.now() - user.last_action > datetime.timedelta(minutes=30):
        user.token = None
        db.commit()
        return None
    user.last_action = datetime.datetime.now()
    db.commit()
    return user


@router.post("/add_post/")
@cache(expire=300)
def add_post(post: PostCreate, db: Session = Depends(get_db)):
    user = get_user(post.token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    new_post = Posts(text=post.text, owner_id=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {'new_post_id': new_post.id}


@router.get("/get_post/")
def add_post(post: PostResponse, db: Session = Depends(get_db)):
    user = get_user(post.token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    post = db.query(User).filter(Posts.id == post.id).first()
    return {'post': post}


@router.delete("/delete_post/")
def delete_post(request: PostResponse, db: Session = Depends(get_db)):
    user = get_user(request.token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    post = db.query(Posts).filter(Posts.id == request.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if user.id != post.owner_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    db.delete(post)
    db.commit()

    return {"detail": "Post deleted"}

