from pydantic import BaseModel

class BlogBase(BaseModel):
    title: str
    content: str

class BlogRequest(BlogBase):
    class Config:
        orm_mode = True



