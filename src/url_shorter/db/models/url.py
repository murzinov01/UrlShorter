from sqlalchemy import Column, Integer, String

from ..config import Base


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    short_url = Column(String, unique=True, index=True)
