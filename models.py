from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_vendor = Column(String, nullable=True)
    parsed_invoice_no = Column(String, nullable=True)
    parsed_date = Column(String, nullable=True)
    parsed_total = Column(String, nullable=True)
    task_id = Column(String, nullable=True, index=True)
    status = Column(String, nullable=True, default='PENDING')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
