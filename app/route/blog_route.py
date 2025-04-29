from fastapi import APIRouter, Depends
from app.repository import blog_repo
from sqlalchemy.orm import Session
from app.models import blog_model
from app.config.database import get_db
from fastapi import Depends
from app.schema import blog_schema

router = APIRouter(prefix="/blog", tags=["Blogs"])

@router.post("/create")
def create_blog(request_blog : blog_schema.BlogRequest, db: Session = Depends(get_db)):
    return blog_repo.create_blog(blog_model.BlogModel(title=request_blog.title, body=request_blog.content), db)


@router.get("/all")
def get_all_blogs(db: Session = Depends(get_db)):
    return blog_repo.get_all_blogs(db)


@router.put("/update/{id}")
def update_blog(id : int, request_blog : blog_schema.BlogRequest, db: Session = Depends(get_db)):
    return blog_repo.update_blog(id, blog_model.BlogModel(title=request_blog.title, body=request_blog.content), db)

@router.delete("/delete/{id}")
def delete_blog(id : int, db: Session = Depends(get_db)):
    return blog_repo.delete_blog(id, db)