from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from model.food import FoodVO


def save(session: Session, vo: FoodVO):
    session.add(vo)
    session.commit()


def save_all(session: Session, xs: list[FoodVO]):
    for x in xs:
        if not session.query(exists().where(FoodVO.id == x.id)).scalar():
            session.add(x)
    session.commit()


def get_all(session: Session):
    return session.query(FoodVO).all()

