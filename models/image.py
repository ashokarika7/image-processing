from sqlalchemy import Column, Integer, String, DateTime
from database.db import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename= Column(String, nullable=True)
    s3_key = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="pending")
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    processing_started_at= Column(DateTime, nullable=True)
    processing_token = Column(String, nullable=True)
