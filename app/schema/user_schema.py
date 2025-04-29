from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str
    password : str

class UserRequest(UserBase):
    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    uuid : str
    name : str
    email : str
    class Config:
        orm_mode = True
