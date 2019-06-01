from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class CategoryRepository:

    def readAll(self):
        """ Read all the categories from the 'database' """
        print("Reading all categories from database...")
        result = session.query(Category).all()
        return result

    def readById(self, id):
        """ Read the category by ID from the 'database' """
        print("Searching for the category with ID: " + str(id))
        result = session.query(Category).filter_by(id=id).first()
        return result

    def create(self, name, user_id):
        if(len(name) < 1):
            print("the name cannot be empty!")
            return
        myFirstCategory = Category(name=name,user_id=user_id)
        session.add(myFirstCategory)
        print("commiting new category with name: " + name)
        session.commit()

    def update(self, categoryId, newName):
        result = session.query(Category).filter_by(id=categoryId).first()
        if (result == []):
            print("The update didn't work!")
            return
        result.name = str(newName)
        session.add(result)
        session.commit()

    def delete(self, categoryId):
        result = session.query(Category).filter_by(
            id=categoryId).first()
        session.delete(result)
        print("The category with ID %s id being deleted" % categoryId)
        session.commit()


class CategoryItemRepository:

    def readAll(self):
        """ Read all the categories from the 'database' """
        print("Reading all categories from database...")
        result = session.query(CategoryItem).all()
        return result

    def readById(self, id):
        """ Read the category by ID from the 'database' """
        print("Searching for the category with ID: " + str(id))
        result = session.query(CategoryItem).filter_by(id=id).first()
        return result

    def readAllByCategoryId(self, category_id):
        """ Read all items by category item  """
        print("Searching for all items in category ID: " + str(category_id))
        result = session.query(CategoryItem).filter_by(category_id=category_id).all()
        return result
    
    def readByCategoryId(self, category_id, item_id):
        """ Read the category item by category ID and item ID """
        print("Searching for the item: " + str(item_id) + "in the category: " + str(category_id))
        result = session.query(CategoryItem).filter_by(id=item_id,category_id=category_id).first()
        return result

    def create(self, name, price, description, user_id, category_id):
        if(len(name) < 1):
            print("the name cannot be empty!")
            return
        newCategoryItem = CategoryItem(name=name, price=price, description=description, user_id=user_id, category_id=category_id)
        session.add(newCategoryItem)
        print("commiting new category with name: " + name)
        session.commit()

    def update(self, categoryId, newName, newPrice, newDescription):
        result = session.query(CategoryItem).filter_by(id=categoryId).first()
        if (result == []):
            print("The update didn't work!")
            return
        result.name = str(newName)
        result.price = str(newPrice)
        result.description = str(newDescription)
        session.add(result)
        session.commit()

    def delete(self, itemId):
        result = session.query(CategoryItem).filter_by(
            id=itemId).first()
        session.delete(result)
        print("The category with ID %s id being deleted" % itemId)
        session.commit()


class UserRepository:

    def readAll(self):
        """ Read all the categories from the 'database' """
        print("Reading all categories from database...")
        result = session.query(User).all()
        return result

    def readById(self, id):
        """ Read the user by ID from the 'database' """
        print("Searching for the user with ID: " + str(id))
        result = session.query(User).filter_by(id=id).first()
        return result

    def getUserID(self, email):
        user = session.query(User).filter_by(email=email).first()
        if user is not None:
            return user.id
        return None

    def create(self, name, email, picture):
        if(len(name) < 1):
            print("the name cannot be empty!")
            return
        myFirstUser = User(name=name, email=email, picture=picture)
        session.add(myFirstUser)
        print("commiting new user with name: " + name)
        session.commit()

    def update(self, userId, newName):
        result = session.query(User).filter_by(id=userId).first()
        if (result == []):
            print("The update didn't work!")
            return
        result.name = str(newName)
        session.add(result)
        session.commit()

    def delete(self, userId):
        result = session.query(User).filter_by(
            id=userId).first()
        session.delete(result)
        print("The user with ID %s id being deleted" % userId)
        session.commit()
