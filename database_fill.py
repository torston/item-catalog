from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, User, CatalogItem

engine = create_engine('sqlite:///item_catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

category = Category(name="Soccer")
session.add(category)
session.commit()

category = Category(name="Basketball")
session.add(category)
session.commit()

category = Category(name="Tennis")
session.add(category)
session.commit()

category = Category(name="Boxing")
session.add(category)
session.commit()

category = Category(name="Running")
session.add(category)
session.commit()

user = User(name="torston",
            email="torston@nomail.com")
session.add(user)
session.commit()

item = CatalogItem(name="Soccer Ball",
                   description="It is a special ball designed to play soccer.",
                   category_id=1,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Soccer Cleat",
                   description="It is a special shoe designed to play soccer "
                               "in grass fields.",
                   category_id=1,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Shin Guard",
                   description="It is a protection gear to protect the shin.",
                   category_id=1,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Goalkeeper Gloves",
                   description="It is a special glove designed to "
                               "catch moving soccer ball.",
                   category_id=1,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Basketball Ball",
                   description="It is a special ball designed to play basketball.",
                   category_id=2,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Basketball Hoop",
                   description="Horizontal circular metal hoop "
                               "supporting a net through which "
                               "players try to throw the basketball.",
                   category_id=2,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Basketball Shoe",
                   description="It is a special shoe to play basketball.",
                   category_id=2,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Tennis Ball",
                   description="It is a special ball designed to play tennis.",
                   category_id=3,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Racket",
                   description="A tennis racket is the racket that you use "
                               "when you play tennis.",
                   category_id=3,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Tennis Shoe",
                   description="It is a special shoe to play tennis.",
                   category_id=3,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Boxing Gloves",
                   description="It is a special padded glove designed for boxing.",
                   category_id=4,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Hand Wrap",
                   description="It is a wrap which is used "
                               "before wearing boxing glove.",
                   category_id=4,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Punching Bag",
                   description="It is a heavy haning bag that "
                               "boxers punch as a triaing.",
                   category_id=4,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Running Shoe",
                   description="It is a special shoe to run without injury.",
                   category_id=5,
                   user_id=1)
session.add(item)
session.commit()

item = CatalogItem(name="Water Bottle",
                   description="It is a water bottle "
                               "which can be carried by runner.",
                   category_id=5,
                   user_id=1)
session.add(item)
session.commit()
