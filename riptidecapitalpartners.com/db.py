import sys, os
INTERP = os.path.join(os.environ['HOME'], 'riptidecapitalpartners.com', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask
from flask_mysqldb import MySQL
import pandas as pd

with open('host.txt') as g:
    hostname = g.read()

with open('dbname.txt') as f:
    var = f.read()

with open('username.txt') as h:
    username = h.read()

with open('pwd.txt') as i:
    pwd = i.read()

application = Flask(__name__)

application.config['MYSQL_HOST'] = hostname
application.config['MYSQL_USER'] = username
application.config['MYSQL_PASSWORD'] = pwd
application.config['MYSQL_DB'] = var

mysql = MySQL(application)

@application.route('/')
def index():
    return 'Hello from Passenger'

@application.route('/testdb')
def data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT firstName FROM MyUsers")
    mysql.connection.commit()
    remaining_rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(remaining_rows)
    return df.to_html(header='true', table_id='table')