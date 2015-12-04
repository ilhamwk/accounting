from flask import *
from playhouse.flask_utils import *

from datetime import datetime, date

from app import app
from model import * 
from helper import *

@app.route('/item', methods=['GET'])
def item_list():
    items = Item.listAll()
    (items, filters, page, pages) = item_filters(request.args, items)
    paginate = Paginate(page, pages, filters, '/item')
    return render_template('item.html',
                           items=items, 
                           date_start=filters['date_start'],
                           date_end=filters['date_end'],
                           store=filters['store'],
                           major=filters['major'],
                           minor=filters['minor'],
                           paginate=paginate)

def item_filters(args, itemQuery):
    retval = { 'store': None, 'minor': None, 'major': None,
               'date_start': None, 'date_end': None}
    if args.get('store'):
        retval['store'] = get_object_or_404(Store, Store.id == args['store'])
        itemQuery = itemQuery.where(Transaction.store == args['store'])
    if args.get('minor'):
        retval['minor'] = get_object_or_404(Minor, Minor.id == args['minor'])
        itemQuery = itemQuery.where(Item.minor == args['minor'])
    if args.get('major'):
        retval['major'] = get_object_or_404(Major, Major.id == args['major'])
        itemQuery = itemQuery.where(Minor.major == args['major'])

    start = date(1990, 1, 1)
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
    if args.get('year') and args.get('month'):
        start = date(year, month, 1)
        end = date(year, month, 1) + relativedelta(months=1) - \
              relativedelta(days=1)
        retval['date_start'] = start
        retval['date_end'] = end
        dateparam = True
    if dateparam:
        itemQuery = itemQuery \
                    .where(Transaction.date >= start.strftime('%Y-%m-%d'),
                           Transaction.date <= end.strftime('%Y-%m-%d'))
    page = int(args['page']) if args.get('page') else 1
    pages = (itemQuery.count() - 1) // app.config['ITEMS_PER_PAGE'] + 1
    itemQuery = itemQuery.paginate(page, app.config['ITEMS_PER_PAGE'])
 
    return (itemQuery, retval, page, pages)

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
        item.note = request.form['note']
        item.save()
        ItemIndex.updateItem(item)
        flash('Item #%s is updated.' % id, 'success')
        return item_detail(id)
    flash('Update item unsuccessful. Missing ID', 'danger')
    return item_list() 

@app.route('/_item/search', methods=['POST'])
def item_search():
    if request.form.get('search_text'):
        words = [word.strip() for word in \
                 request.form['search_text'].split() if word]
        if words:
            search = ' '.join(words)
            items = Item \
                    .select(Item, ItemIndex) \
                    .join(ItemIndex, on=(Item.id == ItemIndex.docid)) \
                    .where(ItemIndex.match(search)) \
                    .order_by(ItemIndex.rank().desc(), Item.id.desc())
            return render_template('item.html', items=items, search=search)

    return item_list() 
 
