from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime

from config import database


class XlsxRequestStatus:
    not_started = "not_started"
    started = "started"
    completed = "completed"


class XlsxRequestVO(database.base):
    __tablename__ = "xlsx_request"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    filename = Column(String)
    food_name = Column(String)
