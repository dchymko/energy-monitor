from flask import Flask, render_template
import random
import datetime
from common.emporia import login_vue, get_all, get_daily

app = Flask(__name__)

@app.route('/')
def home():
    vue = login_vue() 
    vue_data, updated = get_all(vue)[:2]
    updated_datetime = datetime.datetime.fromtimestamp(updated) if updated else None
    return render_template('home.html', vue_data=vue_data, updated=updated_datetime)

@app.route('/daily')
def contact():
    vue = login_vue()
    vue_data = get_daily(vue)
    return render_template('chart.html', vue_data=vue_data)

if __name__ == '__main__':
    app.run(debug=True)