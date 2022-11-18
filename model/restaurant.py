from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from config import database


class RestaurantVO(database.base):
    __tablename__ = "restaurant"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    rating = Column(String)
    rating_count = Column(String)
    delivery_time = Column(String)
    address = Column(String)
    longitude = Column(String)
    latitude = Column(String)
