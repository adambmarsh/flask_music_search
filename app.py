"""
module: app
"""
from flask import Flask, jsonify, redirect, render_template, request

from db_connect import DBConnection
from helpers import build_html


app = Flask(__name__)
app.config['SECRET_KEY'] = 'brian-the-dinosaur'


@app.route('/', methods=['GET', 'POST'])
def index():
    """

    :return:
    """
    return redirect('/ajax')


@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
    """

    :return:
    """
    form_data = request.form
    return render_template('ajax_test.html', form_data=form_data)


@app.route('/form', methods=['POST'])
def form():
    """
    Method to handle HTML form.
    :return: A string containing HTML build from the output of processing the form.
    """
    if not request:
        return 'Error: no request data'

    request_data = request.get_json()
    q = request_data['query']
    search_table = request_data['tables']
    search_columns = request_data['columns']

    db_conn = DBConnection()
    out_data = db_conn.search(user_query=q, table=search_table, columns=search_columns)

    db_conn.close()

    return jsonify({'html': build_html(db_conn.current_schema, out_data, q)})

@app.route('/stream/<filename>',methods=['POST'])
def stream(filename):
    pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
