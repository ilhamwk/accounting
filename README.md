# Accounting 

Personal accounting web-based system in Python.

Requires:

* SQLite
* dominate
* Flask (and Jinja by extension)
* peewee (with playhouse extension)
* jQuery
* Bootstrap + Glyphicons
* Chart.js

To run:

    mkdir receipt; python main.py

This will run an HTTP server in localhost:5000.

CRUD operations for basic data entries are done.

To be added:
* JS support for field input for prices
* Simple backup support (to upload db and receipt pics)

Caveat: In EUR/GBP the item price is encoded as an integer, 100 times its
value, to capture the cents without having to resort to floating point storage.
