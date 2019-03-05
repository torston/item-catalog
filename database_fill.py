from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogUser, CatalogItem

engine = create_engine('sqlite:///item_catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_or_create(db_session, model, **kwargs):
    instance = db_session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db_session.add(instance)
        db_session.commit()
        return instance


user = CatalogUser(name="torston",
            email="torston@nomail.com")
session.add(user)

default_desc = """
Lorem Ipsum is simply dummy text of the printing and 
typesetting industry. Lorem Ipsum has been the industry's standard dummy 
text ever since the 1500s, when an unknown printer took a galley of type and 
scrambled it to make a type specimen book. It has survived not only five 
centuries, but also the leap into electronic typesetting, remaining 
essentially unchanged. It was popularised in the 1960s with the release of 
Letraset sheets containing Lorem Ipsum passages, and more recently with 
desktop publishing software like Aldus PageMaker including versions of Lorem 
Ipsum. 
"""

items = [['Stick', 'Hockey'],
         ['Googles', 'Snowboarding'],
         ['Snowboard', 'Snowboarding'],
         ['Two shinguards', 'Soccer'],
         ['Shinguards', 'Soccer'],
         ['Frisbee', 'Frisbee'],
         ['Bat', 'Baseball'],
         ['Jersey', 'Soccer'],
         ['Soccer Cleats', 'Soccer']]

for item in items:
    category = get_or_create(session, Category, name=item[1])
    item = CatalogItem(name=item[0],
                       description=default_desc,
                       category=category)

    session.add(item)
    session.add(category)

session.commit()
