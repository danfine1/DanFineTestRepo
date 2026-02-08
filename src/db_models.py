from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    is_done = Column(Boolean)