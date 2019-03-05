from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class CatalogUser(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(CatalogUser)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(
        "Category", backref=backref("catalog_items", cascade="all, delete"))

    user_id = Column(Integer, ForeignKey('user.id', ))
    user = relationship(CatalogUser)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.name,
        }


# used check_same_thread = False to avoid threading errors
engine = create_engine('sqlite:///item_catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
