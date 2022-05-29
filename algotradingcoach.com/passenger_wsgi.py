import sys, os

INTERP = os.path.join(os.environ['HOME'], '', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

# https://www.codementor.io/@adityamalviya/python-flask-mysql-connection-rxblpje73
from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm

application = Flask(__name__)

@application.route('/option_chain')
def opt_chain():
    symbol = 'TQQQ'
    ticker = yf.Ticker(symbol)
    exp_dates = ticker.options
    # print(exp_dates)
    df = pd.DataFrame()
    for x in exp_dates:
        opt = ticker.option_chain(x)
        df = df.append(opt.calls, ignore_index=True)
    hist = ticker.history(period="1d", interval="5m")
    df_history = pd.DataFrame(hist)
    recent_value = df_history['Close'].iloc[-1]
    df['recent_px'] = recent_value
    df['intrinsic_value'] = df['recent_px'] - df['strike']
    df['intrinsic_value'] = np.where(df['intrinsic_value'] < 0, 0, df['intrinsic_value'])

    # option price = mid
    # mid = (bid + ask) / 2

    df['option_px'] = (df['bid'] + df['ask']) / 2  # mid options price

    # extrinsic value = option price - intrinsic value

    df['extrinsic_value'] = df['option_px'] - df['intrinsic_value']
    df['extrinsic_value'] = np.where(df['extrinsic_value'] < 0, 0, df['extrinsic_value'])

    # yield = ( extrinsic / recent_px ) * 100

    df['yield'] = (df['extrinsic_value'] / df['recent_px'])
    df['contract_symbol'] = df['contractSymbol'].astype(str)
    df['beginning_index'] = (df['contract_symbol'].str.find('2'))
    df['ending_index'] = (df['beginning_index'] + 6)
    begin_index = df['beginning_index'].iloc[0]
    end_index = df['ending_index'].iloc[0]
    df['expiration_slice'] = df['contract_symbol'].str.slice(begin_index, end_index)

    todays_date = pd.to_datetime('today')
    df['today'] = todays_date

    df['expiration_combined'] = '20' + df['expiration_slice']
    df['converted_expiration'] = pd.to_datetime(df['expiration_combined'])
    df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days

    # number of weeks
    df['number_of_weeks'] = df['days_to_expiration'] / 7

    # weekly yield
    df['weekly_yield'] = np.where(df['number_of_weeks'] < 1, df['yield'], df['yield'] / df['number_of_weeks'])

    # Greeks
    df['T'] = df['days_to_expiration'] / 200

    risk_free_rate = 0.00
    df['r'] = risk_free_rate

    df['v'] = df['impliedVolatility']
    dividend_rate = .00
    df['d'] = dividend_rate
    df['S'] = df['recent_px']
    df['K'] = df['strike']

    df['T_sqrt'] = np.sqrt(df['T'])

    df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df['T']) / (
            df['v'] * df['T_sqrt'])
    df['delta_calc'] = norm.cdf(df['d1'])

    # jjj score
    df['jjj'] = df['weekly_yield'] * df['delta_calc']

    df_two_columns = df[['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj']]

    return df_two_columns.to_html(header='true', table_id='table')


