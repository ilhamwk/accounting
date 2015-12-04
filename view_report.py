from flask import *
from playhouse.flask_utils import *

from datetime import date
from dateutil.relativedelta import relativedelta
import copy

from app import app
from model import Major, Minor, Store, Transaction, Item

FIRST_DATE = date(1900, 1, 1)

def obtain_worth(end_date):
    last_worth = 0
    aggregate = Major.listWithTotalPrice(FIRST_DATE, end_date)
    for major in aggregate:
        if major.income:
            last_worth += major.amount
        else:
            last_worth -= major.amount
    return last_worth

def obtain_aggregate(result):
    income = 0
    expense = 0
    for minor in result:
        if minor.major.income:
            income += minor.amount
        else:
            expense += minor.amount
    return (income, expense)

def init_table():
    majors = Major.listWithMinor().order_by(Major.income.desc(), 
                                            Major.id, Minor.id)
    table = {}
    table['order'] = []
    table['majors'] = []
    prev = None
    for major in majors:
        table['order'].append(major.minor.id)
        if prev == None or prev != major.id: 
            table['majors'].append((major.id, major.income, major.name))
            prev = major.id
        table[major.minor.id] = (major.id, major.name, major.income, 
                                 major.minor.name, 0)
    return table

def simple_minor_table(result):
    table = init_table()
    table['total'] = {}
    for minor_id in table['order']: 
        table['total'][minor_id] = 0 
    for (major_id, _, _) in table['majors']:
        table['total'][('major', major_id)] = 0
    for row in result:
        (major_id, major_name, isIncome, minor_name, _) = table[row.id]
        table[row.id] = (major_id, major_name, isIncome, minor_name, row.amount)
        table['total'][row.id] += row.amount
        table['total'][('major', major_id)] += row.amount
    return table

@app.route('/report', methods=['GET'])
def report_now():
    today = date.today()
    return redirect(url_for('report_month', year=today.year, month=today.month))

@app.route('/report/<int:year>', methods=['GET'])
def report_year(year):
    start = date(year, 1, 1)
    end = date(year + 1, 1, 1) - relativedelta(days=1)
    date_args = 'date_start=%s&date_end=%s' % \
                (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    worth = obtain_worth(end)
    aggregate = Minor.listForReport(start, end)
    (income, expense) = obtain_aggregate(aggregate) 
    result = Minor.listForYearlyReport(year)
    month_table = init_table()
    table = {}
    for month in xrange(1, 13):
        table[month] = copy.deepcopy(month_table)
        table[month]['income'] = 0
        table[month]['expense'] = 0
        for (major, _, _) in table[1]['majors']:
            table[month][('major', major)] = 0
    table['total'] = {}
    table['order'] = table[1]['order']
    table['majors'] = table[1]['majors']
    for minor_id in table['order']: 
        table['total'][minor_id] = 0
    for (major, _, _) in table['majors']:
        table['total'][('major', major)] = 0
    for row in result:
        (major_id, major_name, isIncome, minor_name, _) = table[row.month][row.id]
        table[row.month][row.id] = (major_id, major_name, isIncome, 
                                    minor_name, row.amount)
        table[row.month]['income' if isIncome else 'expense'] += row.amount
        table[row.month][('major', major_id)] += row.amount
        table['total'][row.id] += row.amount
        table['total'][('major', major_id)] += row.amount
    return render_template('report.html', year=year, table=table,
            worth=worth, income=income, expense=expense)

@app.route('/report/<int:year>/<int:month>', methods=['GET'])
def report_month(year, month):
    start = date(year, month, 1)
    end = date(year, month, 1) + relativedelta(months=1) - relativedelta(days=1)
    date_args = '&date_start=%s&date_end=%s' % \
                (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    worth = obtain_worth(end)
    result = Minor.listForReport(start, end)
    (income, expense) = obtain_aggregate(result) 
    table = simple_minor_table(result)
    return render_template('report.html', year=year,
            month=date(1900, month, 1).strftime('%B'), table=table,
            worth=worth, income=income, expense=expense, date_args=date_args)

@app.route('/report/last/<int:days>', methods=['GET'])
def report_last_days(days):
    end = date.today()
    start = end - relativedelta(days=(days-1))
    date_args = '&date_start=%s&date_end=%s' % \
                (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    worth = obtain_worth(end)
    result = Minor.listForReport(start, end)
    (income, expense) = obtain_aggregate(result) 
    table = simple_minor_table(result)
    return render_template('report.html', days=days, table=table,
            worth=worth, income=income, expense=expense, date_args=date_args)


