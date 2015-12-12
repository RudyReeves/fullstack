''' Sets up the catalog using sqlalchemy and declarative_base '''

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False, unique = True)
    user = relationship("Item", cascade = 'delete')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False, unique = True)
    category = relationship("Item", cascade = 'delete')

    def serialize(self):
        items = DBSession().query(Item).filter_by(category_id = self.id).all()
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.serialize() for item in items]
        }

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False, unique = True)
    description = Column(String, nullable = False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'user_id': self.user_id
        }

engine = create_engine("sqlite:///catalog.db")

Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind = engine)