from flask import *
from playhouse.flask_utils import *

from app import app
from model import * 

@app.route('/item', methods=['GET'])
def item_list():
    items = Item.listAll()
    return render_template('item.html', items=items)

@app.route('/item/<int:id>', methods=['GET'])
def item_detail(id):
    item = get_object_or_404(Item, Item.id == id)
    majors = Major.listWithMinor()
    return render_template('item.html', item=item, majors=majors)

@app.route('/_item/delete/<int:id>', methods=['GET'])
def item_delete(id):
    item = get_object_or_404(Item, Item.id == id)
    item.delete_instance()
    flash('Item #%d is deleted.' % id, 'success')
    return jsonify(success=True)

@app.route('/_item/edit', methods=['POST'])
def item_edit():
    if request.form.get('item_id'):
        id = request.form['item_id']
        item = get_object_or_404(Item, Item.id == id)
        item.name = request.form['name']
        item.price = request.form['price']
        item.quantity = request.form['quantity']
        item.minor = request.form['minor_id']
        item.save()
        flash('Item #%d is updated.' % id, 'success')
        return jsonify(success=True)
    flash('Update item unsuccessful. Missing ID', 'danger')
    return jsonify(success=False)

