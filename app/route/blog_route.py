from fastapi import APIRouter, Depends
from app.repository import blog_repo
from sqlalchemy.orm import Session
from app.models import blog_model
from app.config.database import get_db
from fastapi import Depends

router = APIRouter(prefix="/blog", tags=["Blogs"])


@router.post("/create")
def create_blog(title: str, content: str, db: Session = Depends(get_db)):
    return blog_repo.create_blog(blog_model.BlogModel(title=title, body=content), db)
