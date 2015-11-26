# Accounting 

Personal accounting web-based system in Python.

Requires:

* SQLite
* Flask (and Jinja by extension)
* peewee (with playhouse extension)
* jQuery
* Bootstrap + Glyphicons

To run:

    mkdir receipt; python main.py

This will run an HTTP server in localhost:5000.

CRUD operations for basic data entries are done.

To be added:
* Navigation bar
* Reporting
* Search

Caveat: The item price is encoded as an integer, 100 times its value, to capture the cents without having to resort to floating point storage.
