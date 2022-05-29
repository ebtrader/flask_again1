import sys, os

INTERP = os.path.join(os.environ['HOME'], '', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask
import yfinance as yf
import pandas as pd

application = Flask(__name__)

@application.route('/hello')
def opt_chain():
    return 'Hello world'



