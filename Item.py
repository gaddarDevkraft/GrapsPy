from typing import Union, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


# class User(SQLModel, table=True):
#     id: Optional[int] = SQLModel.Field(default = None,primary_key=True)
#     name: str
#     age: Optional[int] = None
#
#
# user_1 = User(id=1, name="John", age=30)
# user_2 = User(id=2, name="John", age=30)
# user_3 = User(id=3, name="John", age=30)
