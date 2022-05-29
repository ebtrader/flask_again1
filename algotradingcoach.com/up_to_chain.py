import sys, os

INTERP = os.path.join(os.environ['HOME'], '', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask
import yfinance as yf

application = Flask(__name__)

@application.route('/chain')
def opt_chain():
    return "Hello World"

@application.route('/test')
def now():
    return "this is a test"

@application.route('/numbers')
def hello():
    ticker = 'NQ=F'
    data = yf.download(tickers=ticker, period='6mo')
    return data.to_html(header='true', table_id='table')




