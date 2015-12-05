from flask import *
from playhouse.flask_utils import *
import string

from app import app
from model import Major, Minor, Store, Transaction, Item

@app.route('/major', methods=['GET', 'POST']) 
def major_list():
    query = Major \
            .select(Major, Minor) \
            .join(Minor, on=(Major.id == Minor.major).alias('minor')) \
            .order_by(Major.id)
    last = None
    minors = []
    majors = []
    for major in query:
        minor = { 'id': major.minor.id, 'name': major.minor.name }
        if last != None and major.id != last.id:
            majors.append({'id': last.id, 'income': last.income, 
                           'name': last.name, 'minors': minors})
            minors = [minor]
        else:
            minors.append(minor)
        last = major
    if last != None:
        majors.append({'id': last.id, 'income': last.income, 
                       'name': last.name, 'minors': minors})
    return render_template('major.html', majors=majors)

@app.route('/major/add', methods=['GET', 'POST'])
def major_add():
    if request.method == 'POST':
        if request.form.get('major_id'):
            major = get_object_or_404(Major, Major.id == request.form['major_id'])
            minors = Minor.listWithStats(request.form['major_id'])
            major.name = request.form['name']
            major.income = bool(request.form.get('income'))
            major.save()
            flash('Category #%d updated successfully.' % major.id, 'success')
        else: 
            major = Major.create(name=request.form['name'],
                                 income=bool(request.form.get('income')))
            minors = []
            for minor_name in string.split(request.form['minors'], ','):
                if len(minor_name) > 0:
                    minor = Minor.create(name=string.strip(minor_name), major=major)
                    minors.append(minor)
            flash('A category created successfully.', 'success')
        return render_template('major.html', major=major, minors=minors)
    return render_template('major.html')

@app.route('/major/<int:id>', methods=['GET', 'POST'])
def major_detail(id):
    major = get_object_or_404(Major, Major.id == id)
    minors = Minor.listWithStats(id)
    num_items = 0
    for minor in minors:
        num_items += minor.count
    return render_template('major.html', 
            major=major, minors=minors, num_items=num_items)

@app.route('/major/delete/<int:id>', methods=['GET', 'POST'])
def major_delete(id):
    major = get_object_or_404(Major, Major.id == id)
    major.delete_instance()
    minors = Minor.delete().where(Minor.major == id).execute()
    flash('Category #%d is deleted.' % id, 'success')
    return jsonify(success=True)

@app.route('/_minor/add', methods=['POST'])
def minor_add():
    try:
        major_id = request.form['major_id']
        major = get_object_or_404(Major, Major.id == major_id)
        minor = Minor.create(name=request.form['name'], major=major)
    except:
        flash('Category #%d not found.' % major_id, 'danger')
        return jsonify(success=False)
    flash('A new subcategory is added.', 'success')
    return jsonify(success=True)

@app.route('/_minor/delete/<int:id>', methods=['GET'])
def minor_delete(id):
    try:
        minor = get_object_or_404(Minor, Minor.id == id)
        minor.delete_instance()
    except:
        return jsonify(success=False)
    return jsonify(success=True)

@app.route('/minor/<int:id>', methods=['GET'])
def minor_detail(id):
    minor = get_object_or_404(Minor, Minor.id == id)
    majors = Major.select().order_by(Major.id)
    return render_template('minor.html', minor=minor, majors=majors)

@app.route('/_minor/edit/<int:id>', methods=['POST'])
def minor_edit(id):
    try:
        minor = Minor.get(Minor.id == id)
        minor.name = request.form['name']
        minor.major = request.form['major_id']
        minor.save()
    except:
        return jsonify(success=False)
    return jsonify(success=True)
