from flask import *
from playhouse.flask_utils import *

from datetime import datetime, date
from hashlib import md5
import os

from app import app
from model import Major, Minor, Store, Transaction, Item, ItemIndex
from helper import *

@app.route('/trans', methods=['GET'])
def trans_list():
    trans = Transaction.listAll()
    (trans, filters, page, pages) = transaction_filters(request.args, trans)
    paginate = Paginate(page, pages, filters, '/trans')
    return render_template('transaction.html', 
                           trans=trans, 
                           date_start=filters['date_start'],
                           date_end=filters['date_end'],
                           store=filters['store'],
                           paginate=paginate)

def transaction_filters(args, transQuery):
    retval = { 'store': None, 'date_start': None, 'date_end': None }
    if args.get('store'):
        retval['store'] = get_object_or_404(Store, Store.id == args['store'])
        transQuery = transQuery.where(Transaction.store == args['store'])
    start = date(1900, 1, 1)
    end = date(9999, 12, 31)
    dateparam = False
    if args.get('date_start'):
        start = datetime.strptime(args['date_start'], '%Y-%m-%d').date()
        retval['date_start'] = start
        dateparam = True
    if args.get('date_end'):
        end = datetime.strptime(args['date_end'], '%Y-%m-%d').date()
        retval['date_end'] = end
        dateparam = True
    if dateparam:
        transQuery = transQuery \
                     .where(Transaction.date >= start.strftime('%Y-%m-%d'), 
                            Transaction.date <= end.strftime('%Y-%m-%d'))
    page = int(args['page']) if args.get('page') else 1
    pages = (transQuery.count() - 1) // app.config['ITEMS_PER_PAGE'] + 1
    transQuery = transQuery.paginate(page, app.config['ITEMS_PER_PAGE'])
    return (transQuery, retval, page, pages)

@app.route('/trans/add', methods=['GET', 'POST'])
def trans_add():
    stores = Store.listAll()
    majors = Major.listWithMinor()
    today = date.today()
    if request.method == 'POST':
        if request.form.get('trans_id'):
            trans_id = request.form['trans_id']
            trans = get_object_or_404(Transaction, Transaction.id == trans_id)
            trans.date = request.form['date']
            trans.store = request.form['store']
            file = request.files['file']
            if file:
                try:
                    filename = hash_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                           filename))
                    remove_file(trans.bill_file_name)
                    trans.bill_file_name = filename
                except:
                    flash('Cannot upload file', 'danger')
            trans.save()
            addNewItems(request.form, trans)
            flash('Successfully updated transaction #%s' % trans_id, 'success')
            items = Item.listTransaction(trans_id)
        else: 
            form_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            store = request.form['store']
            trans = Transaction.create(date=form_date, store=store)
            file = request.files['file']
            if file:
                try:
                    filename = hash_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    trans.bill_file_name = filename
                    trans.save()
                except:
                    flash('Cannot upload file', 'danger')
            items = addNewItems(request.form, trans)
            flash('The transaction is successfully recorded', 'success')
        return render_template('transaction.html', stores=stores, majors=majors,
                transaction=trans, items=items)
    return render_template('transaction.html', stores=stores, majors=majors,
            now=today)

def addNewItems(form, trans):
    item_names = form.getlist('item-name[]')
    item_prices = form.getlist('item-price[]')
    item_quantities = form.getlist('item-quantity[]')
    item_notes = form.getlist('item-note[]')
    item_minors = form.getlist('item-minor[]')
    items = []
    for i in range(len(item_names)):
        if item_names[i] == '':
            break
        item = Item.create(name=item_names[i], 
                           quantity=item_quantities[i],
                           price=item_prices[i],
                           note=item_notes[i],
                           minor=item_minors[i],
                           transaction=trans)
        ItemIndex.storeItem(item)
        items.append(item)
    return items

def hash_filename(filename):
    extension = filename.rsplit('.', 1)[1]
    time = unicode(datetime.now())
    h = md5()
    h.update(filename)
    h.update(time)
    retval = h.hexdigest() + '.' + extension
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], retval)): 
        return hash_filename(filename)
    else:
        return retval

def remove_file(filename):
    if filename != app.config['NO_FILE']:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/trans/<int:id>', methods=['GET'])
def trans_detail(id):
    stores = Store.listAll()
    majors = Major.listWithMinor()
    trans = get_object_or_404(Transaction, Transaction.id == id)
    items = Item.listTransaction(id)
    return render_template('transaction.html', stores=stores, majors=majors,
            transaction=trans, items=items)

@app.route('/trans/bill/<int:id>', methods=['GET'])
def trans_bill(id):
    trans = get_object_or_404(Transaction, Transaction.id == id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               trans.bill_file_name)

@app.route('/_trans/delete/<int:id>', methods=['GET', 'POST'])
def trans_delete(id):
    trans = get_object_or_404(Transaction, Transaction.id == id)
    Item.delete().where(Item.transaction == id).execute()
    remove_file(trans.bill_file_name)
    trans.delete_instance()
    flash('Transaction #%d is deleted.' % id, 'success')
    return jsonify(success=True)

