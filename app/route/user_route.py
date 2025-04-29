from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from fastapi import Depends
from app.models.UserModel import UserModel
from app.repository import user_repo
from app.schema.user_schema import UserRequest

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create")
async def create_user(user_request : UserRequest, db: Session = Depends(get_db)):
    return user_repo.create_user(UserModel(name = user_request.name,email = user_request.email,password = user_request.password), db)