from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String, nullable=False)
    forename = Column(String, nullable=False)
    other_names = Column(Text, nullable=True)  # JSON-encoded list
    email = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
    tags = Column(Text, nullable=True)         # JSON-encoded list
    others = Column(Text, nullable=True)       # JSON-encoded dict

