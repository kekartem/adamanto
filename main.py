from flask import Flask, render_template, request, make_response, redirect
from helpers import *

app = Flask(__name__, static_url_path='/static')

@app.route('/')
async def main():
    return render_template('index.html')


@app.route('/tech/<int:tech_id>')
async def tech(tech_id):
    if tech_id == 1:
        return render_template('tech1.html')
    elif tech_id == 2:
        return render_template('tech2.html')
    elif tech_id == 3:
        return render_template('tech3.html')
    else:
        return redirect('/')
    

@app.route('/getcatalog/', methods=['GET', 'POST'])
async def getcatalog():
    name = request.form.get('name')
    contact_option = request.form.get('option')
    contact = request.form.get('contact')
    add_query(name, contact, 'Получить каталог', contact_option)
    return redirect('/')


@app.route('/submitmessage/', methods=['GET', 'POST'])
async def submitmessage():
    name = request.form.get('name')
    contact = request.form.get('email') + ' / ' + request.form.get('phonenumber')
    message = request.form.get('message')
    add_query(name, contact, message, '-')
    return redirect('/')


@app.route('/allqueries/')
async def allqueries():
    queries = get_all_queries()
    return render_template('allqueries.html', queries=queries)


# @app.route('/catalog/')
# def catalog():
#     return render_template('catalog.html')



app.run(host='0.0.0.0', port=5050, debug=True)