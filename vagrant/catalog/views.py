''' Flask views for the 6 pages on this website '''

import psycopg2
import random, string

from flask import Flask, request, render_template, redirect, url_for, make_response
from flask import session as login_session

import json

import requests
import httplib2
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

from database_setup import Category, Item, User
import db
import gplus
import api

@app.route('/')
@app.route('/catalog')
def index():
    '''Shows categories and latest items'''

    categories = db.get_categories()
    categories = [category.name for category in categories]

    items = db.get_items()
    latest_items = [[item.name, db.get_category_name_by_id(item.category_id)] for item in items] #NOQA

    (state, logged_in, username) = gplus.get_login_state()

    data = {
        'categories': categories,
        'latest_items': latest_items,
        'state': state,
        'logged_in': logged_in,
        'username': username
    }
    return render_template('index.html', data = data)


@app.route('/catalog/<category_name>/items')
def category(category_name):
    '''Shows categories and all items in a selected category'''

    category_id = db.get_category_id_by_name(category_name)
    items = db.get_items_by_category_id(category_id)
    categories = db.get_categories()

    num_items = len(items)
    items_string = 'items'
    if (num_items == 1):
        items_string = 'item'

    (state, logged_in, username) = gplus.get_login_state()

    data = {
        'category_name': category_name,
        'categories': [category.name for category in categories],
        'items': [[db.get_category_name_by_id(item.category_id), item.name] for item in items], #NOQA
        'num_items': num_items,
        'items_string': items_string,
        'state': state,
        'logged_in': logged_in,
        'username': username
    }
    return render_template('category.html', data = data)

@app.route('/catalog/<category_name>/<item_name>')
def item(category_name, item_name):
    '''Shows a specific item's details'''

    item_description = db.get_item_by_name(item_name).description

    (state, logged_in, username) = gplus.get_login_state()
    data = {
        'item_name': item_name,
        'item_description': item_description,
        'state': state,
        'logged_in': logged_in,
        'username': username
    }
    return render_template('item.html', data = data)

@app.route('/catalog/add', methods=['GET', 'POST'])
def add_item():
    '''Adds an item to the database'''

    # Ensure there is a user logged in:
    if not gplus.is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        category_name = request.form['category_name']

        # Ensure the category exists:
        query = db.session.query(Category).filter_by(name = category_name) #NOQA
        if not db.session.query(query.exists()):
            return redirect('/')

        category = query.one()
        item_name = request.form['item_name']
        item_description = request.form['item_description']

        # Validate the item name and descriptions
        if not db.is_valid_item(item_name, item_description):
            return redirect('/')

        user_id = db.get_user_id_by_name(login_session['username'])
        db.create_item(item_name, item_description, category.id, user_id)

        return redirect("/catalog/%s/items" % category_name)
    elif request.method == 'GET':
        categories = db.get_categories()

        (state, logged_in, username) = gplus.get_login_state()
        data = {
            'categories': [category.name for category in categories],
            'state': state,
            'logged_in': logged_in,
            'username': username
        }
        return render_template('add.html', data = data)

@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    '''Allows a logged-in user to edit an item they created'''

    # Ensure there is a user logged in:
    if not gplus.is_logged_in():
        return redirect('/')

    # Ensure the item being edited exists:
    query = db.session.query(Item).filter_by(name = item_name)
    if not db.session.query(query.exists()):
        return redirect('/')

    # Ensure the logged-in user owns this item:
    item = query.one()
    if item.user_id != login_session['user_id']:
        return redirect('/')

    if request.method == 'POST':
        new_item_name = request.form['item_name']
        new_item_description = request.form['item_description']
        new_category_name = request.form['category_name']

        # Ensure the new category exists:
        query = db.session.query(Category).filter_by(name = new_category_name)
        if not db.session.query(query.exists()):
            return redirect('/')

        new_category = query.one()

        # Validate the new item name and description
        if not db.is_valid_item(new_item_name, new_item_description):
            return redirect('/catalog/%s/%s' % (new_category.name, item_name))

        item.name = new_item_name
        item.description = new_item_description
        item.category_id = new_category.id
        db.session.commit()
        return redirect('/catalog/%s/%s' % (new_category.name, new_item_name))
    elif request.method == 'GET':
        item_description = db.session.query(Item).filter_by(name = item_name).one().description #NOQA

        categories = db.get_categories()
        categories = [category.name for category in categories]

        (state, logged_in, username) = gplus.get_login_state()

        data = {
            'item_name': item_name,
            'item_description': item_description,
            'categories': categories,
            'state': state,
            'logged_in': logged_in,
            'username': username
        }
        return render_template('edit.html', data = data)

@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    '''Allows a logged-in user to delete an item they created'''

    # Ensure there is a user logged in:
    if not gplus.is_logged_in():
        return redirect('/')

    # Ensure the item being edited exists:
    query = db.session.query(Item).filter_by(name = item_name)
    if not db.session.query(query.exists()):
        return redirect('/')

    # Ensure the logged-in user owns this item:
    item = query.one()
    if item.user_id != login_session['user_id']:
        return redirect('/')

    if request.method == 'POST':
        category_id = item.category_id
        category_name = db.get_category_name_by_id(category_id)
        db.session.delete(item)
        return redirect('/catalog/%s/items' % category_name)
    elif request.method == 'GET':
        (state, logged_in, username) = gplus.get_login_state()

        data = {
            'item_name': item_name,
            'state': state,
            'logged_in': logged_in,
            'username': username
        }
        return render_template('delete.html', data = data)