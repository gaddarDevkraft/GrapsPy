from starlette.exceptions import HTTPException
from app.models.UserModel import UserModel
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def create_user(user_request: UserModel, db: Session):
    exiting_user = db.query(UserModel).filter(UserModel.email == user_request.email)
    if exiting_user.first():
        return HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail=f"User with email {user_request.email} already exit!")

    new_user = UserModel(name=user_request.name, email=user_request.email, password=user_request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user