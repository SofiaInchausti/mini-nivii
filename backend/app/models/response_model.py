from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.models.database import Base


class Response(Base):
    __tablename__ = "response"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    question = Column(String)
    chart = Column(String)
    chart_data = Column(Text, nullable=True)
    sql_query = Column(String)
    result = Column(String)
    status = Column(String)  # "success" o "error"
    error_message = Column(String, nullable=True)
