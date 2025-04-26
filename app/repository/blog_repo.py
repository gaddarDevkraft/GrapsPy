from starlette.exceptions import HTTPException

from app.models import blog_model
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def create_blog(blog_request: blog_model.BlogModel, db: Session):
    new_blog = blog_model.BlogModel(title=blog_request.title, body=blog_request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


def get_all_blogs(db: Session):
    all_blogs = db.query(blog_model.BlogModel).all()
    return all_blogs


def update_blog(id: int, blog_request: blog_model.BlogModel, db: Session):
    blog_to_update = db.query(blog_model.BlogModel).filter(blog_model.BlogModel.id == id).first()

    if not blog_to_update:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found")

    blog_to_update.title = blog_request.title
    blog_to_update.body = blog_request.body
    db.commit()
    db.refresh(blog_to_update)
    return blog_to_update


