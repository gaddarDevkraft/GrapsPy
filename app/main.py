from typing import Union
from fastapi import FastAPI, status

app = FastAPI()


@app.get("/")
def hello():
    return {"status": "RAG operation"}


# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host = "0.0.0.0", port = 8000)
