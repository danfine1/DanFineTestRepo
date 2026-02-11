from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.sql import func


class LinkModel(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    target_url = Column(String, unique=True, index=True, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    total_clicks = Column(Integer, nullable=False, default=0)
    total_earnings = Column(Numeric(10, 2), nullable=False, default=0)


class LinkClickModel(Base):
    __tablename__ = "link_clicks"

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("links.id"), index=True, nullable=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
