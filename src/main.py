from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends

from models import Item
from database import engine, SessionLocal
import db_models
app = FastAPI()
db_models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dp_dependency = Annotated[SessionLocal, Depends(get_db)]
@app.get("/")
def root(db: dp_dependency):
    return db.query(db_models.ItemModel).all()

@app.post("/items")
def create_item(item: Item, db: dp_dependency):
    db_item = db_models.ItemModel(name=item.name, description=item.description, is_done=item.is_done)
    db.add(db_item)
    db.commit()

@app.get("/items/{item_name}")
def read_item(item_name: str, db: dp_dependency):
    db_item = db.query(db_models.ItemModel).filter(db_models.ItemModel.name == item_name).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_name}")
def update_item(item_name: str, item: Item, db: dp_dependency):
    db_item = db.query(db_models.ItemModel).filter(db_models.ItemModel.name == item_name).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # make sure the new item's name doesn't already exist in the db
    exists_in_db = db.query(db_models.ItemModel).filter(db_models.ItemModel.name == item.name).first()
    if exists_in_db:
        raise HTTPException(status_code=400, detail="Item with the same name already exists in db")

    db_item.name = item.name
    db_item.description = item.description
    db_item.is_done = item.is_done

    db.commit()
    db.refresh(db_item)
    return db_item

