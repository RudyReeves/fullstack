#!/usr/bin/env python
#
# application.py -- A web server with a catalog_json of categories containing items
# Author: Rudy Reeves

from db import clear_database, create_category
from views import app

# TODO: CSS styling

if __name__ == '__main__':
    clear_database()

    test_category_1 = create_category("test_category_1")
    test_category_2 = create_category("test_category_2")

    app.secret_key = "lRYRXEimZGfbt3Q2TpD_6_Kj"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
