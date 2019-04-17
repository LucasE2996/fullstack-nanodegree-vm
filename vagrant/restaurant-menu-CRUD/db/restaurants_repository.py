from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class RestaurantRepository:

    def readAll(self):
        """ Read all the restaurants from the 'database' """
        print("Reading all restaurants from database...")
        result = session.query(Restaurant).all()
        return result

    def readById(self, id):
        """ Read the restaurant by ID from the 'database' """
        print("Searching for the restaurant with ID: " + str(id))
        result = session.query(Restaurant).filter_by(id=id).one()
        return result

    def create(self, restaurantName):
        if(len(restaurantName) < 1):
            print("the name cannot be empty!")
            return
        myFirstRestaurant = Restaurant(name=restaurantName)
        session.add(myFirstRestaurant)
        print("commiting new restaurant with name: " + restaurantName)
        session.commit()

    def update(self, restaurantId, newName):
        result = session.query(Restaurant).filter_by(id=restaurantId).one()
        if (result == []):
            print("The update didn't work!")
            return
        result.name = str(newName)
        session.add(result)
        session.commit()

    def delete(self, restaurantId):
        result = session.query(Restaurant).filter_by(
            id=restaurantId).one()
        session.delete(result)
        print("The restaurant with ID %s id being deleted" % restaurantId)
        session.commit()
