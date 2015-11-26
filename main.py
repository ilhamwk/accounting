from app import app
from model import *
from view_item import *
from view_major import *
from view_report import *
from view_store import *
from view_transaction import *

if __name__ == '__main__':
    Major.create_table(fail_silently=True)
    Minor.create_table(fail_silently=True)
    Store.create_table(fail_silently=True)
    Transaction.create_table(fail_silently=True)
    Item.create_table(fail_silently=True)
    ItemIndex.create_table(fail_silently=True)
    app.run(debug=True)
