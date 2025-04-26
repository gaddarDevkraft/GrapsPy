from app.models import blog_model
from sqlalchemy.orm import Session


def create_blog(blog_request : blog_model.BlogModel, db : Session):
    new_blog = blog_model.BlogModel(title = blog_request.title, body = blog_request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog




