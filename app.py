# -*- coding: utf-8 -*-

import os

from flask import Flask
from micawber import bootstrap_basic
from playhouse.sqlite_ext import SqliteExtDatabase

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(APP_ROOT, 'acc.db')
DEBUG = True
SECRET_KEY = '9688ba2e18571a9fe989c2e3c5414ecd' # md5 of "accounting". Change as necessary.

app = Flask(__name__)
app.config.from_object(__name__)
db = SqliteExtDatabase(app.config['DATABASE'], threadlocals=True)
oembed = bootstrap_basic()

app.config['COUNTRY'] = 'DE'
app.config['NO_FILE'] = 'empty'
app.config['ITEMS_PER_PAGE'] = 50
app.config['UPLOAD_FOLDER'] = 'receipts'

@app.template_filter('datefilter')
def datefilter(date, fmt='%Y-%m-%d'):
    return date.strftime(fmt)

@app.template_filter('pricefilter')
def pricefilter(price, fmt=None):
    if (price == None):
        price = 0
    if app.config['COUNTRY'] == 'DE':
        p = int(price) / 100.0
        return unicode('{:20,.2f}'.format(p) + ' €', 'utf8') 
    elif app.config['COUNTRY'] == 'ID':
        p = int(price)
        return 'Rp. ' + '{:20,d}'.format(p)
