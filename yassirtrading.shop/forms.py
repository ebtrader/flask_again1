import sys, os

INTERP = os.path.join(os.environ['HOME'], '', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask, render_template, request
import yfinance as yf
from flask_mysqldb import MySQL
import pandas as pd
from scipy.signal import argrelextrema
import plotly
import plotly.graph_objects as go
import numpy as np
import json

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

@application.route('/chain')
def opt_chain():
    return "Hello World"

@application.route('/numbers')
def hello():
    ticker = 'NQ=F'
    data = yf.download(tickers=ticker, period='6mo')
    return data.to_html(header='true', table_id='table')

@application.route('/testdb')
def data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT firstName FROM MyUsers")
    mysql.connection.commit()
    remaining_rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(remaining_rows)
    return df.to_html(header='true', table_id='table')

@application.route('/chart', methods=['GET', 'POST'])
def graph():
    if request.method == "POST":
        details = request.form

        ticker = details['ticker']

        df = yf.download(tickers=ticker, period='6mo', interval='1d')
        #df = yf.download(tickers = ticker, start='2013-01-01', end='2014-12-31')

        df = df.reset_index()

        Order = 5

        max_idx = argrelextrema(df['Close'].values, np.greater, order=Order)[0]
        min_idx = argrelextrema(df['Close'].values, np.less, order=Order)[0]


        fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                              open=df['Open'],
                                              high=df['High'],
                                              low=df['Low'],
                                              close=df['Close'])])
        Size = 10
        Width = 1

        fig1.add_trace(
            go.Scatter(
                mode='markers',
                x=df.iloc[max_idx]['Date'],
                y=df.iloc[max_idx]['High'],
                marker=dict(
                    color='darkred',
                    size=Size,
                    line=dict(
                        color='MediumPurple',
                        width=Width
                    )
                ),
                showlegend=False
            )
        )

        fig1.add_trace(
            go.Scatter(
                mode='markers',
                x=df.iloc[min_idx]['Date'],
                y=df.iloc[min_idx]['Low'],
                marker=dict(
                    color='forestgreen',
                    size=Size,
                    line=dict(
                        color='MediumPurple',
                        width=Width
                    )
                ),
                showlegend=False
            )
        )

        # fig1.show()

        fig1.update_layout(
            title=ticker, xaxis_rangeslider_visible=False
        )

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('ticker.html')
