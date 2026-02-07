from pydantic import BaseModel

class Item(BaseModel):
    name: str = None
    description: str = None
    is_done: bool = False