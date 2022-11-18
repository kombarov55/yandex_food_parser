from sqlalchemy.orm import Session

from model.restaurant import RestaurantVO


def save(session: Session, restaurant: RestaurantVO) -> RestaurantVO:
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant
