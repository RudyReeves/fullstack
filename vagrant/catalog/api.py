''' JSON and XML API endpoints for the catalog '''

from flask import jsonify, make_response
from lxml import etree, objectify
import json

import views
import db

@views.app.route('/catalog.json')
def catalog_json():
    '''Returns a JSON-ified representation of the catalog database'''
    categories = db.session.query(views.Category).all()
    return jsonify(catalog = [category.serialize() for category in categories]) #NOQA

@views.app.route('/catalog.xml')
def catalog_xml():
    ''' Returns an XML-serialized representation of the catalog database: '''
    root = objectify.Element("catalog")
    categories = db.session.query(views.Category).all()
    for category in categories:
        category_element = objectify.Element(category.name, id = str(category.id)) #NOQA
        items = db.session.query(views.Item).filter_by(category_id = category.id).all() #NOQA
        for item in items:
            item_element = objectify.Element(item.name,
                                             id = str(item.id),
                                             description = item.description,
                                             category_id = str(item.category_id)) #NOQA

            category_element.append(item_element)

        root.append(category_element)

    objectify.deannotate(root, pytype = True, xsi = True)
    xml = etree.tostring(root, pretty_print = True)

    response= make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response