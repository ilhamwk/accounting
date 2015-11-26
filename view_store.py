from flask import *
from playhouse.flask_utils import *

from app import app
from model import Major, Minor, Store, Transaction, Item

@app.route('/store', methods=['GET'])
def store_list():
    stores = Store.listWithStats()
    return render_template('store.html', stores=stores)

@app.route('/store/<int:id>', methods=['GET'])
def store_detail(id):
    store = get_object_or_404(Store, Store.id == id)
    trans = Transaction.listStoreTransactions(id)
    if request.args.get('page'):
        trans.paginate(request.args['page'], 
                       app.config['ITEMS_PER_PAGE'])
    return render_template('transaction.html', store=store, trans=trans)

@app.route('/_store/add', methods=['GET', 'POST'])
def store_add():
    if request.method == 'POST':
        if request.form.get('store_id'):
            store = get_object_or_404(Store, Store.id == request.form['store_id'])
            store.name = request.form['name']
            store.save()
            flash('Store #%d updated successfully.' % (store.id,), 'success')
        else:
            name = request.form['name']
            if name == "":
                flash('Store needs to have a name', 'danger')
            else:
                store = Store.create(name=name)
                flash('Store %s created successfully.' % (name,), 'success')
        return jsonify(success=True) 
    return render_template('store.html')
   
@app.route('/_store/delete/<int:id>', methods=['POST'])
def store_delete(id):
    store = get_object_or_404(Store, Store.id == id)
    name = store.name
    store.delete_instance()
    flash('Store %s is deleted.' % (name,), 'success')
    return jsonify(success=True)

