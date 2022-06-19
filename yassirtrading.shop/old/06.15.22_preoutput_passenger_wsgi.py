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

@application.route('/simple')
def output_simple():
    out_text = 'hello world now'
    return render_template('output.html', arithmetic=out_text)

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

        period = details['period']
        interval = details['interval']

        df = yf.download(tickers=ticker, period=period, interval=interval)
        #df = yf.download(tickers = ticker, start='2013-01-01', end='2014-12-31')

        df = df.reset_index()

        Order = 5

        max_idx = argrelextrema(df['Close'].values, np.greater, order=Order)[0]
        min_idx = argrelextrema(df['Close'].values, np.less, order=Order)[0]


        fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                              open=df['Open'],
                                              high=df['High'],
                                              low=df['Low'],
                                              close=df['Close'], showlegend=False)])
        Size = 15
        Width = 1

        fig1.add_trace(
            go.Scatter(
                name='Sell Here!',
                mode='markers',
                x=df.iloc[max_idx]['Date'],
                y=df.iloc[max_idx]['High'],
                marker=dict(
                    symbol=46,
                    color='darkred',
                    size=Size,
                    line=dict(
                        color='MediumPurple',
                        width=Width
                    )
                ),
                showlegend=True
            )
        )

        fig1.add_trace(
            go.Scatter(
                name='Buy Here!',
                mode='markers',
                x=df.iloc[min_idx]['Date'],
                y=df.iloc[min_idx]['Low'],
                marker=dict(
                    symbol=45,
                    color='forestgreen',
                    size=Size,
                    line=dict(
                        color='MediumPurple',
                        width=Width
                    )
                ),
                showlegend=True
            )
        )

        # fig1.show()

        fig1.update_layout(
            title=ticker, xaxis_rangeslider_visible=False
        )

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('dropdown.html')

@application.route('/calculatortqqq', methods=['GET', 'POST'])
def tqqq_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "TQQQ"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'NQ=F'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculatortna', methods=['GET', 'POST'])
def tna_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "TNA"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'RTY=F'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculatorfas', methods=['GET', 'POST'])
def fas_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "FAS"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'XLF'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculatorupro', methods=['GET', 'POST'])
def upro_target():
    if request.method == "POST":
        details = request.form

        target = details['ticker']
        target = int(target)
        tqqq_ticker = "UPRO"

        df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
        recent_tqqq = df_tqqq['Close'].iloc[-1]
        # print(df_tqqq['Close'])
        # print(recent_tqqq)

        nq_ticker = 'ES=F'
        df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
        recent_nq = df_nq['Close'].iloc[-1]
        # print(df_nq['Close'])
        # print(recent_nq)


        nq_current = recent_nq
        tqqq_current = recent_tqqq
        nq_target = target
        tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
        # print(tqqq_target)
        tqqq_display = str(tqqq_target)
        df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
        return df.to_html(header='true', table_id='table')
    return render_template('target.html')

@application.route('/calculator', methods=['GET', 'POST'])
def dropdown_fn():
    if request.method == "POST":
        details = request.form

        target = details['target']
        target = float(target)
        ticker_input = details['ticker']

        if ticker_input == "UPRO":
            tqqq_ticker = ticker_input

            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period ='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'ES=F'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period ='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)


            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1)* tqqq_current
            # print(tqqq_target)
            tqqq_display = str(tqqq_target)
            df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        elif ticker_input == "TQQQ":
            tqqq_ticker = ticker_input

            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'NQ=F'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)

            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1) * tqqq_current
            # print(tqqq_target)
            tqqq_display = str(tqqq_target)
            df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        elif ticker_input == "TNA":
            tqqq_ticker = ticker_input

            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'RTY=F'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)

            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1) * tqqq_current
            # print(tqqq_target)
            tqqq_display = str(tqqq_target)
            df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        elif ticker_input == "FAS":
            tqqq_ticker = ticker_input
            df_tqqq = yf.download(tickers=tqqq_ticker, interval='5m', period='1d')
            recent_tqqq = df_tqqq['Close'].iloc[-1]
            # print(df_tqqq['Close'])
            # print(recent_tqqq)

            nq_ticker = 'XLF'
            df_nq = yf.download(tickers=nq_ticker, interval='5m', period='1d')
            recent_nq = df_nq['Close'].iloc[-1]
            # print(df_nq['Close'])
            # print(recent_nq)

            nq_current = recent_nq
            tqqq_current = recent_tqqq
            nq_target = target
            tqqq_target = ((nq_target / nq_current - 1) * 3 + 1) * tqqq_current
            # print(tqqq_target)
            tqqq_display = str(tqqq_target)
            df = pd.DataFrame(data=[tqqq_ticker, tqqq_display])
            # print(df)

        return df.to_html(header='true', table_id='table')
    return render_template('dropdown_ticker.html')
