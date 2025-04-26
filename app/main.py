from typing import Union
from fastapi import FastAPI, status, APIRouter, Depends
from app.config.database import engine, SessionLocal
import app.models.TestingModel as testing_model
import app.crud_operation.crud as crud

app = FastAPI()

testing_model.Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def api():
    return {"status": "running.."}

@app.post("/create_model")
def create_testing(name : str, email : str, db : SessionLocal = Depends(get_db)):
    return crud.create_testing_model(db, name, email)





#for the debugging
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host = "0.0.0.0", port = 8000)
