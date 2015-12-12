''' Helper functions for DB operations '''

from database_setup import DBSession
from database_setup import User, Item, Category

session = DBSession()

def clear_database():
    session.query(User).delete()
    session.query(Item).delete()
    session.query(Category).delete()
    session.commit()

def create_category(name):
    category = Category(name = name)
    session.add(category)
    session.commit()
    return category

def create_user(login_session):
    username = login_session['username']
    new_user = User(name = username)
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(name = username).one()
    return user.id

def create_item(name, description, category_id, user_id):
    item = Item(name = name, description = description, category_id = category_id, user_id = user_id)
    session.add(item)
    session.commit()
    return item

def get_category_name_by_id(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    return category.name

def get_category_id_by_name(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    return category.id

def get_categories():
    return session.query(Category).all()

def get_items():
    return session.query(Item).all()

def get_item_by_name(name):
    return session.query(Item).filter_by(name = name).one()

def get_items_by_category_id(category_id):
    return session.query(Item).filter_by(category_id = category_id).all()

def get_user_by_name(name):
    return session.query(User).filter_by(name = name).one()

def get_user_id_by_name(name):
    try:
        user = session.query(User).filter_by(name = name).one()
        return user.id
    except:
        return None

def is_valid_item(item_name, item_description):
    '''Validates an item after creation/edit'''
    if (item_name == ''):
        return False
    if (item_description == ''):
        return False
    return True
