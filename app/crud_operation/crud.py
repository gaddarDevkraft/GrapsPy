from sqlalchemy.orm import Session
from app.models.TestingModel import TestingModel

def create_testing_model(db: Session, name : str, email : str):
    testing_data = TestingModel(name = name,email =  email)
    db.add(testing_data)
    db.commit()
    db.refresh(testing_data)
    return testing_data


