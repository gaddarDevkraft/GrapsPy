from typing import Union
from fastapi import FastAPI, status
from Item import Item
from sqlalchemy import create_engine

app = FastAPI()


@app.get("/")
def hello():
    return {"data": {"gaddar", "arman"}}


@app.get("/{name}")
def hello_name(name: str, q: Union[str, None] = None):
    if name is None:
        name = "world"
    return {"name": name, "q": q}


@app.post(path="/items", status_code = status.HTTP_201_CREATED, )
def create_item(item: Item):
    return item

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
