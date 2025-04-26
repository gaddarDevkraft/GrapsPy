from sqlalchemy import Column, Integer, String, DateTime
from app.config.database import BASE
from sqlalchemy.sql import func


class BlogModel(BASE):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    body = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
