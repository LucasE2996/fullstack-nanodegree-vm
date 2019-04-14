from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# CREATE


def create():
    myFirstRestaurant = Restaurant(name="Pizza Palace")
    session.add(myFirstRestaurant)
    sesssion.commit()

# READ


def read():
    "Example one"
    firstResult = session.query(Restaurant).first()
    print(firstResult.name)
    "Example two"
    items = session.query(MenuItem).all()
    for item in items:
        print item.name

# UPDATE


def update():
    veggieBurgers = session.query(MenuItem).filter_by(name='Veggie Burger')
    for veggieBurger in veggieBurgers:
        print veggieBurger.id
        print veggieBurger.price
        print veggieBurger.restaurant.name
        print "\n"


# DELETE

def delete():
    spinach = session.query(MenuItem).filter_by(name='Spinach Ice Cream').one()
    session.delete(spinach)
    session.commit()


if __name__ == "__main__":
    read()
