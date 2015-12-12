# catalog
A web app presenting a catalog of items, using Python's Flask and SQLAlchemy frameworks.

# Requirements
* Python (v2.7+)
* Python libraries (see pg_config.sh)
* VirtualBox (https://www.virtualbox.org/)
* Vagrant (https://www.vagrantup.com/)
* Flask (http://flask.pocoo.org/)

# Server Startup
1. cd into the "/vagrant/catalog" directory on your local machine
2. Run "vagrant up" (and wait)
3. Run "vagrant ssh" (and wait)
4. cd into "/vagrant/catalog" again (this is the virtual directory)
5. On first startup, run "python database_setup.py" (this sets up the database)
6. Run "python application.py" (this starts the server)

# Usage
* Navigate to "localhost:8000" in your browser. Create/view/edit/delete items as you wish.
* Retrieve the JSON-formatted catalog from "localhost:8000/catalog.json"
* Retrieve the XML-formatted catalog from "localhost:8000/catalog.xml"
