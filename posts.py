from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from schemas import PostCreate, PostResponse
from data_base import get_db
from models import User, Posts
import datetime

router = APIRouter()


def get_user(token: str, db: Session):
    """ 
    Get the user from the database using the token.

    Args:
        token (str): The user's token.
        db (Session): The database session.

    Returns:
        User: The user object if the token is valid, otherwise None.
    """
    user = db.query(User).filter(User.token == token).first()
    if datetime.datetime.now() - user.last_action > datetime.timedelta(minutes=30):
        user.token = None
        db.commit()
        return None
    user.last_action = datetime.datetime.now()
    db.commit()
    return user


@router.post("/add_post/")
def add_post(post: PostCreate, db: Session = Depends(get_db)):
    """
    Add a new post.

    Args:
        post (PostCreate): The post information.
        db (Session): The database session.

    Returns:
        dict: The ID of the newly created post.

    Raises:
        HTTPException: If the token is invalid.
    """
    user = get_user(post.token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    new_post = Posts(text=post.text, owner_id=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {'new_post_id': new_post.id}


@router.get("/get_post/")
@cache(expire=300)
def get_post(post: PostResponse, db: Session = Depends(get_db)):
    """
    Get a post by ID.

    Args:
        post (PostResponse): The post request containing the post ID and token.
        db (Session): The database session.

    Returns:
        dict: The post information.

    Raises:
        HTTPException: If the token is invalid or the post is not found.
    """
    user = get_user(post.token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    post = db.query(User).filter(Posts.id == post.id).first()
    return {'post': post}


@router.delete("/delete_post/")
def delete_post(request: PostResponse, db: Session = Depends(get_db)):
    """
    Delete a post by ID.

    Args:
        request (PostResponse): The post request containing the post ID and token.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful deletion.

    Raises:
        HTTPException: If the token is invalid, the post is not found, or the user does not have permission.
    """
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

