from flask import *
from peewee import *
from playhouse.sqlite_ext import *

from datetime import date, time

from app import db, app

class Major(Model):
    name = CharField()
    income = BooleanField(default = False)

    class Meta:
        database = db

    @staticmethod
    def listWithMinor():
        return Major \
               .select(Major, Minor) \
               .join(Minor) \
               .order_by(Major.id, Minor.id)

    @staticmethod
    def listWithTotalPrice(date_start, date_end):
        return Major \
               .select(Major, fn.SUM(Item.price).alias('amount')) \
               .join(Minor) \
               .join(Item, JOIN.LEFT_OUTER) \
               .join(Transaction, JOIN.LEFT_OUTER) \
               .where(date_start.strftime('%Y-%m-%d') <= Transaction.date,
                      date_end.strftime('%Y-%m-%d') >= Transaction.date) \
               .group_by(Minor) \
               .order_by(Major.income, Major.id)


class Minor(Model):
    name = CharField()
    major = ForeignKeyField(Major, related_name='major_category')

    class Meta:
        database = db

    @staticmethod
    def listWithStats(major_id):
        return Minor \
               .select(Minor, fn.COUNT(Item.id).alias('count')) \
               .join(Item, JOIN.LEFT_OUTER) \
               .where(Minor.major == major_id) \
               .group_by(Minor) \
               .order_by(Minor.id)

    @staticmethod
    def listForReport(date_start, date_end):
        return Minor \
               .select(Minor, Major, fn.SUM(Item.price).alias('amount')) \
               .join(Major) \
               .switch(Minor) \
               .join(Item, JOIN.LEFT_OUTER) \
               .join(Transaction, JOIN.LEFT_OUTER) \
               .where(Transaction.date >= date_start,
                      Transaction.date <= date_end)  \
               .group_by(Minor) \
               .order_by(Major.income, Major.id, Minor.id)

    @staticmethod
    def listForYearlyReport(year):
        return Minor \
               .select(Transaction.date.month.alias('month'), Major, Minor, 
                       fn.SUM(Item.price).alias('amount')) \
               .join(Major) \
               .switch(Minor) \
               .join(Item, JOIN.LEFT_OUTER) \
               .join(Transaction, JOIN.LEFT_OUTER) \
               .where(year == Transaction.date.year) \
               .group_by(Minor, Transaction.date.month) \
               .order_by(Transaction.date.month,
                         Major.income, Major.id, Minor.id)
 
    @staticmethod
    def assetUntilDate(date_end):
        date_start = date(1900, 1, 1)
        return Minor.listForReport(date_start, date_end)


class Store(Model):
    name = CharField()

    class Meta:
        database = db

    @staticmethod
    def listWithStats():
        return Store \
               .select(Store, fn.COUNT(Transaction.id).alias('num_trans'), 
                       fn.COUNT(Item.id).alias('num_items')) \
               .join(Transaction, JOIN.LEFT_OUTER) \
               .join(Item, JOIN.LEFT_OUTER) \
               .group_by(Store.id) \
               .order_by(Store.id)

    @staticmethod
    def listAll():
        return Store.select().order_by(Store.id)


class Transaction(Model):
    date = DateField()
    store = ForeignKeyField(Store, related_name = 'store_origin', index = True)
    bill_file_name = TextField(default = app.config['NO_FILE'])
    
    class Meta:
        database = db

    @staticmethod
    def listStoreTransactions(store_id):
        return Transaction.listAll().where(Transaction.store == store_id)

    @staticmethod
    def listAll():
        return Transaction \
               .select(Transaction, Store, fn.COUNT(Item.id).alias('items'), 
                       fn.SUM(Item.price).alias('price')) \
               .join(Store) \
               .switch(Transaction) \
               .join(Item, JOIN.LEFT_OUTER) \
               .group_by(Transaction.id) \
               .order_by(Transaction.id)


class Item(Model):
    name = CharField(index = True)
    quantity = DoubleField()
    price = IntegerField()
    note = TextField(index = True)
    minor = ForeignKeyField(Minor, related_name='minor_category')
    transaction = ForeignKeyField(Transaction, related_name='transaction_id')

    class Meta:
        database = db

    @staticmethod
    def listMajor(major_id):
        return Item.listAll().where(Major.id == major_id)

    @staticmethod
    def listMinor(minor_id):
        return Item.listAll().where(Minor.id == minor_id)

    @staticmethod
    def listTransaction(trans_id):
        return Item.listAll().where(Transaction.id == trans_id)

    @staticmethod
    def listAll():
        return Item \
               .select(Item, Transaction, Store, Minor.name, Major.name) \
               .join(Transaction) \
               .join(Store) \
               .switch(Item) \
               .join(Minor) \
               .join(Major) \
               .order_by(Item.id)


class ItemIndex(FTSModel):
    name = SearchField()
    note = SearchField()

    class Meta:
        database = db
        options = {'tokenize': 'porter'}

    @staticmethod
    def storeItem(item):
        ItemIndex.insert({
            ItemIndex.docid: item.id,
            ItemIndex.name: item.name,
            ItemIndex.note: item.note}).execute()

    @staticmethod
    def updateItem(item):
        ItemIndex.update(name=item.name) \
                 .update(note=item.note) \
                 .where(docid == item.id) \
                 .execute()


