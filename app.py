# -*- coding: utf-8 -*-

from dominate.tags import * 
from flask import Flask, request
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, View, Subgroup
from flask_nav.renderers import Renderer
from micawber import bootstrap_basic
from playhouse.sqlite_ext import SqliteExtDatabase

import os
from datetime import date

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
    p = int(price) / 100.0
    if app.config['COUNTRY'] == 'DE':
        return unicode('{:20,.2f}'.format(p) + ' €', 'utf8') 
    elif app.config['COUNTRY'] == 'UK':
        return unicode('{:20,.2f}'.format(p) + ' £', 'utf8') 
    elif app.config['COUNTRY'] == 'ID':
        return 'Rp. ' + '{:20,d}'.format(int(price))

nav = Nav()
@nav.renderer()
class NavRenderer(Renderer):
    def visit_Navbar(self, node):
        sub = []
        for item in node.items:
            sub.append(self.visit(item))

        return ul('', *sub, cls='nav navbar-nav')

    def visit_View(self, node):
        cls = ''
        # a hack to get the active right
        if node.active or (request.path[:5] == node.get_url()[:5] 
                           and request.path[:5] != '/repo'):
            cls = 'active'
        return li(a(node.text, href=node.get_url()), cls=cls)

    def visit_Subgroup(self, node):
        dropdown = ul(cls='dropdown-menu')
        for item in node.items:
            dropdown += self.visit(item)
        toggle = a(node.title, cls='dropdown-toggle', data_toggle='dropdown',
                   role='button')
        toggle['aria-haspopup'] = 'true'
        toggle['aria-expanded'] = 'false'
        toggle.add(span('', cls='caret'))
        li_name = li(toggle, cls='dropdown')
        li_name.add(dropdown) 
        return li_name

@nav.navigation()
def mynavbar():
    return Navbar('accounting',
            Subgroup('Reports',
                View('This month', 'report_now'),
                View('This year', 'report_year', year=date.today().year),
                View('Last year', 'report_year', year=date.today().year-1),
                View('Last 30 days', 'report_last_days', days=30),
                View('Last 90 days', 'report_last_days', days=90),
                ),
            View('Transactions', 'trans_list'),
            View('Items', 'item_list'),
            View('Stores', 'store_list'),
            View('Categories', 'major_list'),
            )
nav.init_app(app)
