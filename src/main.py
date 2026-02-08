from fastapi import FastAPI, HTTPException
from models import Item
app = FastAPI()

items: list[Item] = []

@app.get("/")
def root():
    return items

@app.post("/items")
def create_item(item: Item) -> list[Item]:
    items.append(item)
    return items

@app.get("/items/{item_index}")
def read_item_at_index(item_index: int) -> Item:
    if item_index < 0 or item_index >= len(items):
        raise HTTPException(status_code=404, detail="Item index out of range")
    return items[item_index]

@app.get("/items")
def get_all_items() -> list[Item]:
    return items