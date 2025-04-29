from sqlalchemy import Column, Integer, String, DateTime
from app.config.database import BASE
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserModel(BASE):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=lambda : str(uuid.uuid4()))
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


