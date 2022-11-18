from sqlalchemy import Column, Integer, String, ForeignKey

from config import database


class FoodVO(database.base):
    __tablename__ = "food"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer)
    name = Column(String)
    description = Column(String)
    src = Column(String)
    price = Column(String)
    weight = Column(String)
