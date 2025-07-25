from pydantic import BaseModel
from datetime import datetime


class ResponseCreate(BaseModel):
    date: datetime
    chart: str


class ResponseRead(ResponseCreate):
    id: int

    class Config:
        orm_mode = True
