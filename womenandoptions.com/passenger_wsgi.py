import sys, os

INTERP = os.path.join(os.environ['HOME'], '', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

# https://www.codementor.io/@adityamalviya/python-flask-mysql-connection-rxblpje73
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
import plotly
import plotly.graph_objects as go
import json
from datetime import timedelta
from finta import TA
import math

application = Flask(__name__)

application.config['MYSQL_HOST'] =
application.config['MYSQL_USER'] =
application.config['MYSQL_PASSWORD'] =
application.config['MYSQL_DB'] =

mysql = MySQL(application)


@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        details = request.form
        firstName = details['fname']
        lastName = details['lname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO MyUsers(firstName, lastName) VALUES (%s, %s)", (firstName, lastName))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template('index.html')


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


@application.route('/ticker', methods=['GET', 'POST'])
def ticker_form():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
        ticker = yf.Ticker(symbol)
        exp_dates = ticker.options
        # print(exp_dates)
        df = pd.DataFrame()
        for x in exp_dates:
            opt = ticker.option_chain(x)
            df = df.append(opt.calls, ignore_index=True)
        return df.to_html(header='true', table_id='table')
    return render_template('ticker.html')


@application.route('/tickeroptions', methods=['GET', 'POST'])
def ticker_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj']]

        # max_expiration = 12-03-2021
        # min_delta = float(details['min_delta'])
        # min_strike = 150
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= max_expiration, :]
        return df_two_columns.to_html(header='true', table_id='table')
    return render_template('ticker.html')


@application.route('/chain', methods=['GET', 'POST'])
def chain_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj']]

        # max_expiration = 12-03-2021
        # min_delta = float(details['min_delta'])
        # min_strike = float(details['strike'])
        min_yield = float(details['yield'])
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= max_expiration, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta.to_html(header='true', table_id='table')
    return render_template('yield.html')


@application.route('/yield', methods=['GET', 'POST'])
def yield_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj']]

        # max_expiration = 12-03-2021
        # min_delta = float(details['min_delta'])
        # min_strike = float(details['strike'])
        min_yield = float(details['yield'])
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= max_expiration, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta.to_html(header='true', table_id='table')
    return render_template('yield.html')


@application.route('/expiration', methods=['GET', 'POST'])
def exp_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj',
             'converted_expiration']]

        # max_expiration = 12-03-2021
        # min_delta = float(details['min_delta'])
        # min_strike = float(details['strike'])
        # min_yield = float(details['yield'])
        min_exp = str(details['exp'])
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= min_exp, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= max_expiration, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta.to_html(header='true', table_id='table')
    return render_template('expiration.html')


@application.route('/delta', methods=['GET', 'POST'])
def delta_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj',
             'converted_expiration']]

        # max_expiration = 12-03-2021
        min_delta = float(details['delta'])
        # min_strike = float(details['strike'])
        # min_yield = float(details['yield'])
        # min_exp = str(details['exp'])
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= min_exp, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= max_expiration, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta.to_html(header='true', table_id='table')
    return render_template('delta.html')


@application.route('/delta_and_expiration', methods=['GET', 'POST'])
def delta_and_exp_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj',
             'converted_expiration']]

        # max_expiration = 12-03-2021
        min_delta = float(details['delta'])
        # min_strike = float(details['strike'])
        # min_yield = float(details['yield'])
        min_exp = str(details['exp'])
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= min_exp, :]
        find_delta_and_exp = find_delta.loc[lambda find_delta: find_delta['converted_expiration'] <= min_exp, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta_and_exp.to_html(header='true', table_id='table')
    return render_template('delta_and_expiration.html')


@application.route('/delta_exp_yield', methods=['GET', 'POST'])
def delta_exp_yield_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1'])

        # jjj score
        df['jjj'] = df['weekly_yield'] * df['delta_calc']

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj',
             'converted_expiration']]

        # max_expiration = 12-03-2021
        min_delta = float(details['delta'])
        # min_strike = float(details['strike'])
        min_yield = float(details['yield'])
        min_exp = str(details['exp'])
        # min_strike = int(details['min_strike'])
        # min_delta = 0.2
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= min_exp, :]
        find_delta_and_exp = find_delta.loc[lambda find_delta: find_delta['converted_expiration'] <= min_exp, :]
        find_delta_and_exp_yield = find_delta_and_exp.loc[
                                   lambda find_delta_and_exp: find_delta_and_exp['weekly_yield'] > min_yield, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta_and_exp_yield.to_html(header='true', table_id='table')
    return render_template('delta_and_expiration_and_yield.html')


@application.route('/delta_exp_yield_strike', methods=['GET', 'POST'])
def delta_exp_yield_strike_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1']).round(2)

        # jjj score
        df['jjj'] = ((df['weekly_yield'] * df['delta_calc']) * 100).round(2)

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj',
             'converted_expiration']]

        # max_expiration = 12-03-2021
        min_delta = float(details['delta'])
        min_strike = float(details['strike'])
        min_yield = float(details['yield'])
        min_exp = str(details['exp'])
        # min_delta = 0.2
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= min_exp, :]
        find_delta_and_exp = find_delta.loc[lambda find_delta: find_delta['converted_expiration'] <= min_exp, :]
        find_delta_and_exp_yield = find_delta_and_exp.loc[
                                   lambda find_delta_and_exp: find_delta_and_exp['weekly_yield'] > min_yield, :]
        find_delta_and_exp_yield_strike = find_delta_and_exp_yield.loc[
                                          lambda find_delta_and_exp_yield: find_delta_and_exp_yield[
                                                                               'strike'] > min_strike, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta_and_exp_yield_strike.to_html(header='true', table_id='table')
    return render_template('delta_expiration_yield_strike.html')


@application.route('/yassir', methods=['GET', 'POST'])
def yassir_options():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
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

        df['extrinsic_value'] = (df['option_px'] - df['intrinsic_value']).round(2)
        df['extrinsic_value'] = np.where(df['extrinsic_value'] < 0, 0, df['extrinsic_value'])

        # yield = ( extrinsic / recent_px ) * 100

        df['yield'] = ((df['extrinsic_value'] / df['recent_px'])).round(3)

        # i am calculating the date here out of the options symbol
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
        df['days_to_expiration'] = (df['converted_expiration'] - df['today']).dt.days + 1

        # number of weeks
        df['number_of_weeks'] = df['days_to_expiration'] / 7

        # weekly yield
        df['weekly_yield'] = (
            np.where(df['number_of_weeks'] < 1, df['yield'], df['yield'] / df['number_of_weeks'])).round(3)

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

        df['d1'] = (np.log(df['S'].astype(float) / df['K']) + ((df['r'] - df['d']) + df['v'] * df['v'] / 2) * df[
            'T']) / (
                           df['v'] * df['T_sqrt'])
        df['delta_calc'] = norm.cdf(df['d1']).round(2)

        # jjj score
        df['jjj'] = ((df['weekly_yield'] * df['delta_calc']) * 100).round(2)

        df_two_columns = df[
            ['contractSymbol', 'strike', 'extrinsic_value', 'yield', 'weekly_yield', 'delta_calc', 'jjj',
             'converted_expiration']]

        # max_expiration = 12-03-2021
        min_delta = float(details['delta'])
        min_strike = float(details['strike'])
        min_yield = float(details['yield'])
        min_exp = str(details['exp'])
        # min_delta = 0.2
        find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['delta_calc'] > min_delta, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['strike'] > min_strike, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['weekly_yield'] > min_yield, :]
        # find_delta = df_two_columns.loc[lambda df_two_columns: df_two_columns['converted_expiration'] <= min_exp, :]
        find_delta_and_exp = find_delta.loc[lambda find_delta: find_delta['converted_expiration'] <= min_exp, :]
        find_delta_and_exp_yield = find_delta_and_exp.loc[
                                   lambda find_delta_and_exp: find_delta_and_exp['weekly_yield'] > min_yield, :]
        find_delta_and_exp_yield_strike = find_delta_and_exp_yield.loc[
                                          lambda find_delta_and_exp_yield: find_delta_and_exp_yield[
                                                                               'strike'] > min_strike, :]
        # return df_two_columns.to_html(header='true', table_id='table')
        return find_delta_and_exp_yield_strike.to_html(header='true', table_id='table')
    return render_template('delta_expiration_yield_strike.html')


@application.route('/plotting', methods=['GET', 'POST'])
def yassir_plotting():
    ticker = 'NQ=F'

    df = yf.download(tickers=ticker, period='2y', interval='1d')

    df = df.reset_index()

    # print(df)

    fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                          open=df['Open'],
                                          high=df['High'],
                                          low=df['Low'],
                                          close=df['Close'])]

                     )


    graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('notdash.html', graphJSON=graphJSON)

@application.route('/forecast', methods=['GET', 'POST'])
def forecast_plotting():
    ticker = "TQQQ"

    # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
    data = yf.download(tickers=ticker, period="1y", interval='1d')

    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

    df1 = pd.DataFrame(data)

    df = df1.reset_index()

    df7 = df.rename(
        columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'},
        inplace=False)

    df7.to_csv('daily.csv')

    n = 5

    df3 = df7.groupby(np.arange(len(df7)) // n).max()
    # print('df3 max:', df3)

    df4 = df7.groupby(np.arange(len(df7)) // n).min()
    # print('df4 min:', df4)

    df5 = df7.groupby(np.arange(len(df7)) // n).first()
    # print('df5 open:', df5)

    df6 = df7.groupby(np.arange(len(df7)) // n).last()
    # print('df6 close:', df6)

    agg_df = pd.DataFrame()

    agg_df['date'] = df6['date']
    agg_df['low'] = df4['low']
    agg_df['high'] = df3['high']
    agg_df['open'] = df5['open']
    agg_df['close'] = df6['close']

    # print(agg_df)

    df2 = agg_df

    # print(df2)
    num_periods = 21
    df2['SMA'] = TA.SMA(df2, 21)
    df2['FRAMA'] = TA.FRAMA(df2, 10)
    df2['WMA'] = TA.WMA(df2, 9)
    df2['TEMA'] = TA.TEMA(df2, num_periods)
    # df2['VWAP'] = TA.VWAP(df2)

    # ATR

    num_periods_ATR = 21
    multiplier = 1

    df2['ATR_diff'] = df2['high'] - df2['low']
    df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
    df2['Line'] = df2['WMA'].round(2)
    df2['line_change'] = df2['Line'] / df2['Line'].shift(1)
    df3 = pd.DataFrame()
    df3['date'] = df2['date']
    df3['close'] = df2['line_change']
    df3['open'] = df2['line_change']
    df3['high'] = df2['line_change']
    df3['low'] = df2['line_change']

    # calculate projection angle
    periods_change = 5  # drives the projection

    df3['change_SMA'] = TA.WMA(df3, periods_change)  # drives the projection
    df2['change_SMA'] = df3['change_SMA']

    df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
    df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

    multiplier_1 = 1.6
    multiplier_2 = 2.3

    df2['upper_band_1'] = (df2['Line'] + multiplier_1 * df2['ATR']).round(2)
    df2['lower_band_1'] = (df2['Line'] - multiplier_1 * df2['ATR']).round(2)

    df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR'].round(2)
    df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR'].round(2)

    # try the loop again
    bars_back = 10
    date_diff = df2.loc[len(df2) - 1, 'date'] - df2.loc[len(df2) - 2, 'date']

    line_diff = df2.loc[len(df2) - 1, 'change_SMA']

    def date_by_adding_business_days(from_date, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:  # sunday = 6
                continue
            business_days_to_add -= 1
        return current_date

    counter = 0
    bars_out = 20
    while counter < bars_out:
        df2.loc[len(df2), 'Line'] = df2.loc[len(df2) - 1, 'Line'] * line_diff
        df2.loc[len(df2) - 1, 'date'] = date_by_adding_business_days(df2.loc[len(df2) - 2, 'date'], n)
        counter += 1

    multiplier_projection = .6
    multiplier_1_projection = .8
    multiplier_2_projection = 1.2

    ATR = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_projection
    ATR_1 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_1_projection
    ATR_2 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_2_projection

    counter1 = 0
    while counter1 < bars_out:
        df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_1'] = df2.loc[len(
            df2) - bars_out - 1 + counter1, 'Line'] + ATR_1
        df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_1'] = df2.loc[len(
            df2) - bars_out - 1 + counter1, 'Line'] - ATR_1
        df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_2'] = df2.loc[len(
            df2) - bars_out - 1 + counter1, 'Line'] + ATR_2
        df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_2'] = df2.loc[len(
            df2) - bars_out - 1 + counter1, 'Line'] - ATR_2
        df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band'] = df2.loc[len(
            df2) - bars_out - 1 + counter1, 'Line'] + ATR
        df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band'] = df2.loc[len(
            df2) - bars_out - 1 + counter1, 'Line'] - ATR

        counter1 += 1

    recent_price = df2['close'].iloc[-bars_out - 1]
    # print(recent_price)
    df2['recent_px'] = recent_price
    df2['dist_to_upper'] = df2['upper_band'] / df2['recent_px'] - 1
    df2['dist_to_lower'] = df2['lower_band'] / df2['recent_px'] - 1
    df2['dist_to_line'] = df2['Line'] / df2['recent_px'] - 1

    etf_data = yf.download(tickers=ticker, period='5d', interval='1d')
    etf_df = pd.DataFrame(etf_data)
    recent_etf = etf_df['Close'].iloc[-1]
    # print(recent_etf)
    df2['etf'] = recent_etf
    df2['etf_upper'] = df2['etf'] * (1 + df2['dist_to_upper'] * 3)
    df2['etf_lower'] = df2['etf'] * (1 + df2['dist_to_lower'] * 3)
    df2['etf_line'] = df2['etf'] * (1 + df2['dist_to_line'] * 3)

    selected_range = df2[['date', 'etf', 'etf_line', 'etf_upper', 'etf_lower']].tail(21).round(2)
    # print(selected_range)
    # selected_range.to_csv('selected.csv')

    df2.to_csv("gauss.csv")

    # https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

    # https://plotly.com/python/legend/#legend-item-names

    # fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

    fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                          open=df2['open'],
                                          high=df2['high'],
                                          low=df2['low'],
                                          close=df2['close'])]

                     )

    fig1.add_trace(
        go.Scatter(
            x=df2['date'],
            y=df2['upper_band'].round(2),
            name='upper band',
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=True)
    )

    fig1.add_trace(
        go.Scatter(
            x=df2['date'],
            y=df2['lower_band'].round(2),
            name='lower band',
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=True)
    )

    fig1.add_trace(
        go.Scatter(
            x=df2['date'],
            y=df2['upper_band_1'].round(2),
            name='upper band_1',
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=True)
    )

    fig1.add_trace(
        go.Scatter(
            x=df2['date'],
            y=df2['lower_band_1'].round(2),
            name='lower band_1',
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=True)
    )

    fig1.add_trace(
        go.Scatter(
            x=df2['date'],
            y=df2['Line'],
            name="WMA",
            mode="lines",
            line=go.scatter.Line(color="blue"),
            showlegend=True)
    )

    fig1.update_layout(
        hovermode='x unified'
    )

    graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('notdash.html', graphJSON=graphJSON)

@application.route('/chooseticker', methods=['GET', 'POST'])
def choose_a_ticker():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
        ticker = str(symbol)
        # ticker = yf.Ticker(symbol)

        # ticker = "TQQQ"

        # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
        data = yf.download(tickers=ticker, period="1y", interval='1d')

        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

        df1 = pd.DataFrame(data)

        df = df1.reset_index()

        df7 = df.rename(
            columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'},
            inplace=False)

        df7.to_csv('daily.csv')

        n = 5

        df3 = df7.groupby(np.arange(len(df7)) // n).max()
        # print('df3 max:', df3)

        df4 = df7.groupby(np.arange(len(df7)) // n).min()
        # print('df4 min:', df4)

        df5 = df7.groupby(np.arange(len(df7)) // n).first()
        # print('df5 open:', df5)

        df6 = df7.groupby(np.arange(len(df7)) // n).last()
        # print('df6 close:', df6)

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        # print(agg_df)

        df2 = agg_df

        # print(df2)
        num_periods = 21
        df2['SMA'] = TA.SMA(df2, 21)
        df2['FRAMA'] = TA.FRAMA(df2, 10)
        df2['WMA'] = TA.WMA(df2, 9)
        df2['TEMA'] = TA.TEMA(df2, num_periods)
        # df2['VWAP'] = TA.VWAP(df2)

        # ATR

        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
        df2['Line'] = df2['WMA'].round(2)
        df2['line_change'] = df2['Line'] / df2['Line'].shift(1)
        df3 = pd.DataFrame()
        df3['date'] = df2['date']
        df3['close'] = df2['line_change']
        df3['open'] = df2['line_change']
        df3['high'] = df2['line_change']
        df3['low'] = df2['line_change']

        # calculate projection angle
        periods_change = 5  # drives the projection

        df3['change_SMA'] = TA.WMA(df3, periods_change)  # drives the projection
        df2['change_SMA'] = df3['change_SMA']

        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 2.3

        df2['upper_band_1'] = (df2['Line'] + multiplier_1 * df2['ATR']).round(2)
        df2['lower_band_1'] = (df2['Line'] - multiplier_1 * df2['ATR']).round(2)

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR'].round(2)
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR'].round(2)

        # try the loop again
        bars_back = 10
        date_diff = df2.loc[len(df2) - 1, 'date'] - df2.loc[len(df2) - 2, 'date']

        line_diff = df2.loc[len(df2) - 1, 'change_SMA']

        def date_by_adding_business_days(from_date, add_days):
            business_days_to_add = add_days
            current_date = from_date
            while business_days_to_add > 0:
                current_date += timedelta(days=1)
                weekday = current_date.weekday()
                if weekday >= 5:  # sunday = 6
                    continue
                business_days_to_add -= 1
            return current_date

        counter = 0
        bars_out = 20
        while counter < bars_out:
            df2.loc[len(df2), 'Line'] = df2.loc[len(df2) - 1, 'Line'] * line_diff
            df2.loc[len(df2) - 1, 'date'] = date_by_adding_business_days(df2.loc[len(df2) - 2, 'date'], n)
            counter += 1

        multiplier_projection = multiplier
        multiplier_1_projection = multiplier_1
        multiplier_2_projection = multiplier_2

        ATR = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_projection
        ATR_1 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_1_projection
        ATR_2 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_2_projection

        counter1 = 0
        while counter1 < bars_out:
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_1'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR_1
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_1'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR_1
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_2'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR_2
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_2'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR_2
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR

            counter1 += 1

        recent_price = df2['close'].iloc[-bars_out - 1]
        # print(recent_price)
        df2['recent_px'] = recent_price
        df2['dist_to_upper'] = df2['upper_band'] / df2['recent_px'] - 1
        df2['dist_to_lower'] = df2['lower_band'] / df2['recent_px'] - 1
        df2['dist_to_line'] = df2['Line'] / df2['recent_px'] - 1

        etf_data = yf.download(tickers=ticker, period='5d', interval='1d')
        etf_df = pd.DataFrame(etf_data)
        recent_etf = etf_df['Close'].iloc[-1]
        # print(recent_etf)
        df2['etf'] = recent_etf
        df2['etf_upper'] = df2['etf'] * (1 + df2['dist_to_upper'] * 3)
        df2['etf_lower'] = df2['etf'] * (1 + df2['dist_to_lower'] * 3)
        df2['etf_line'] = df2['etf'] * (1 + df2['dist_to_line'] * 3)

        selected_range = df2[['date', 'etf', 'etf_line', 'etf_upper', 'etf_lower']].tail(21).round(2)
        # print(selected_range)
        # selected_range.to_csv('selected.csv')

        df2.to_csv("gauss.csv")

        # https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

        # https://plotly.com/python/legend/#legend-item-names

        # fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'])]

                         )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band'].round(2),
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band'].round(2),
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band_1'].round(2),
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band_1'].round(2),
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['Line'],
                name="WMA",
                mode="lines",
                line=go.scatter.Line(color="blue"),
                showlegend=True)
        )

        fig1.update_layout(
            hovermode='x unified',
            title=symbol
        )

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('notdash.html', graphJSON=graphJSON)
    return render_template('ticker.html')

@application.route('/barsback', methods=['GET', 'POST'])
def bars_back():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
        ticker = str(symbol)
        # ticker = yf.Ticker(symbol)

        # ticker = "TQQQ"

        # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
        data = yf.download(tickers=ticker, period="1y", interval='1d')

        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

        df1 = pd.DataFrame(data)

        df = df1.reset_index()

        df7 = df.rename(
            columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'},
            inplace=False)

        df7.to_csv('daily.csv')

        n = 5

        df3 = df7.groupby(np.arange(len(df7)) // n).max()
        # print('df3 max:', df3)

        df4 = df7.groupby(np.arange(len(df7)) // n).min()
        # print('df4 min:', df4)

        df5 = df7.groupby(np.arange(len(df7)) // n).first()
        # print('df5 open:', df5)

        df6 = df7.groupby(np.arange(len(df7)) // n).last()
        # print('df6 close:', df6)

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        # print(agg_df)

        df2 = agg_df

        # print(df2)
        num_periods = 21
        df2['SMA'] = TA.SMA(df2, 21)
        df2['FRAMA'] = TA.FRAMA(df2, 10)
        df2['WMA'] = TA.WMA(df2, 9)
        df2['TEMA'] = TA.TEMA(df2, num_periods)
        # df2['VWAP'] = TA.VWAP(df2)

        # ATR

        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
        df2['Line'] = df2['WMA'].round(2)
        df2['line_change'] = df2['Line'] / df2['Line'].shift(1)
        df3 = pd.DataFrame()
        df3['date'] = df2['date']
        df3['close'] = df2['line_change']
        df3['open'] = df2['line_change']
        df3['high'] = df2['line_change']
        df3['low'] = df2['line_change']

        # calculate projection angle
        periods_change = int(details['periodschange'])  # drives the projection

        df3['change_SMA'] = TA.WMA(df3, periods_change)  # drives the projection
        df2['change_SMA'] = df3['change_SMA']

        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 2.3

        df2['upper_band_1'] = (df2['Line'] + multiplier_1 * df2['ATR']).round(2)
        df2['lower_band_1'] = (df2['Line'] - multiplier_1 * df2['ATR']).round(2)

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR'].round(2)
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR'].round(2)

        # try the loop again
        bars_back = 10
        date_diff = df2.loc[len(df2) - 1, 'date'] - df2.loc[len(df2) - 2, 'date']

        line_diff = df2.loc[len(df2) - 1, 'change_SMA']

        def date_by_adding_business_days(from_date, add_days):
            business_days_to_add = add_days
            current_date = from_date
            while business_days_to_add > 0:
                current_date += timedelta(days=1)
                weekday = current_date.weekday()
                if weekday >= 5:  # sunday = 6
                    continue
                business_days_to_add -= 1
            return current_date

        counter = 0
        bars_out = 20
        while counter < bars_out:
            df2.loc[len(df2), 'Line'] = df2.loc[len(df2) - 1, 'Line'] * line_diff
            df2.loc[len(df2) - 1, 'date'] = date_by_adding_business_days(df2.loc[len(df2) - 2, 'date'], n)
            counter += 1

        multiplier_projection = multiplier
        multiplier_1_projection = multiplier_1
        multiplier_2_projection = multiplier_2

        ATR = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_projection
        ATR_1 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_1_projection
        ATR_2 = df2.loc[len(df2) - bars_out - 1, 'ATR'] * multiplier_2_projection

        counter1 = 0
        while counter1 < bars_out:
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_1'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR_1
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_1'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR_1
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_2'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR_2
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_2'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR_2
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR

            counter1 += 1

        recent_price = df2['close'].iloc[-bars_out - 1]
        # print(recent_price)
        df2['recent_px'] = recent_price
        df2['dist_to_upper'] = df2['upper_band'] / df2['recent_px'] - 1
        df2['dist_to_lower'] = df2['lower_band'] / df2['recent_px'] - 1
        df2['dist_to_line'] = df2['Line'] / df2['recent_px'] - 1

        etf_data = yf.download(tickers=ticker, period='5d', interval='1d')
        etf_df = pd.DataFrame(etf_data)
        recent_etf = etf_df['Close'].iloc[-1]
        # print(recent_etf)
        df2['etf'] = recent_etf
        df2['etf_upper'] = df2['etf'] * (1 + df2['dist_to_upper'] * 3)
        df2['etf_lower'] = df2['etf'] * (1 + df2['dist_to_lower'] * 3)
        df2['etf_line'] = df2['etf'] * (1 + df2['dist_to_line'] * 3)

        selected_range = df2[['date', 'etf', 'etf_line', 'etf_upper', 'etf_lower']].tail(21).round(2)
        # print(selected_range)
        # selected_range.to_csv('selected.csv')

        df2.to_csv("gauss.csv")

        # https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

        # https://plotly.com/python/legend/#legend-item-names

        # fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'])]

                         )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band'].round(2),
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band'].round(2),
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band_1'].round(2),
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band_1'].round(2),
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                )
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['Line'],
                name="WMA",
                mode="lines",
                line=go.scatter.Line(color="blue"),
                )
        )

        fig1.update_layout(
            hovermode='x unified',
            title=symbol,
            showlegend=False,
            width=2000,
            height=1200
        )

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('notdash.html', graphJSON=graphJSON)
    return render_template('barsback.html')

@application.route('/currentTQQQ')
def TQQQcurrent():
    ticker = "TQQQ"

    # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
    data = yf.download(tickers=ticker, period="1y", interval='1d')

    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

    df1 = pd.DataFrame(data)

    df2 = df1.reset_index()

    fig1 = go.Figure(data=[go.Candlestick(x=df2['Date'],
                                          open=df2['Open'],
                                          high=df2['High'],
                                          low=df2['Low'],
                                          close=df2['Close'])]

                     )

    fig1.add_shape(type="rect",
                   x0='2021-08-30', y0=146, x1='2021-09-10', y1=152,
                   line=dict(
                       color="LightSeaGreen",
                       width=2,
                   ),
                   fillcolor="RoyalBlue", opacity=0.4,

                   )

    fig1.add_shape(type="rect",
                   x0='2021-12-03', y0=144, x1='2021-12-22', y1=168,
                   line=dict(
                       color="LightSeaGreen",
                       width=2,
                   ),
                   fillcolor="RoyalBlue", opacity=0.4,

                   )

    fig1.add_shape(type="line",
                   x0='2021-08-31', y0=145, x1='2021-12-21', y1=145,
                   line=dict(
                       color="LightSeaGreen",
                       width=4,
                       dash='dashdot',

                   ),
                   )

    fig1.add_shape(type="line",
                   x0='2021-12-07', y0=168, x1='2021-12-21', y1=168,
                   line=dict(
                       color="LightSeaGreen",
                       width=4,
                       dash='dashdot',

                   ),
                   )

    fig1.add_shape(type="line",
                   x0='2021-11-23', y0=183, x1='2021-12-21', y1=183,
                   line=dict(
                       color="LightSeaGreen",
                       width=4,
                       dash='dashdot',

                   ),
                   )

    fig1.add_annotation(x='2021-12-14', y=168,
                        text="1st Target",
                        showarrow=True,
                        arrowhead=1)

    fig1.add_annotation(x='2021-12-09', y=183,
                        text="2nd Target",
                        showarrow=True,
                        arrowhead=1)

    fig1.update_shapes(dict(xref='x', yref='y'))

    fig1.update_layout(hovermode='x', spikedistance=-1, width=1800, height=1200)

    # fig1.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True)

    fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                      ticks='inside', nticks=40)
    graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('notdash.html', graphJSON=graphJSON)

@application.route('/neckline', methods=['GET', 'POST'])
def neck_line():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
        ticker = str(symbol)
        # ticker = yf.Ticker(symbol)

        # ticker = "TQQQ"

        # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
        data = yf.download(tickers=ticker, period="1y", interval='1d')

        df = pd.DataFrame(data)

        df = df.reset_index()

        df['Date'] = df['Date'].astype(str)

        # print(df)

        df['WMA'] = TA.WMA(df, 9)

        # print(df)

        # Calculate the difference between rows

        # https://www.codeforests.com/2020/10/04/calculate-date-difference-between-rows/

        df['WMA_diff'] = df['WMA'].diff()

        # print(df)

        # https://stackoverflow.com/questions/32984462/setting-1-or-0-to-new-pandas-column-conditionally
        # 1 or 0 switch

        df['slope'] = df['WMA_diff'] > 0

        # print(df)

        df['slope'] = df['slope'].astype(int)

        # print(df)

        # https://newbedev.com/comparing-previous-row-values-in-pandas-dataframe

        df['trigger'] = df['slope'].eq(df['slope'].shift())

        df['trigger'] = df['trigger'].astype(int)

        df['neckline_trigger'] = (df['trigger'] == 0) & (df['slope'] > 0)

        df['neckline_trigger'] = df['neckline_trigger'].astype(int)

        # df['rolling_min'] = df['Low'].rolling(window=3).min().shift(1).fillna(0)

        df['rolling_min'] = df['Low'].rolling(window=4).min().fillna(0)

        df['vertex'] = np.where(df['neckline_trigger'], df['rolling_min'], 0)

        df['sell'] = (df['trigger'] == 0) & (df['slope'] == 0)

        df['sell'] = df['sell'].astype(int)

        # df['rolling_max'] = df['High'].rolling(window=3).max().shift(1).fillna(0)

        df['rolling_max'] = df['High'].rolling(window=4).max().fillna(0)

        df['roll_max_trigger'] = df['rolling_max'].eq(df['rolling_max'].shift())

        df['roll_max_trigger'] = df['roll_max_trigger'].astype(int)

        df['roll_max_date_bool'] = (df['roll_max_trigger'] == 0)

        df['roll_max_date'] = df['Date'].where(df['roll_max_date_bool'])

        df['roll_max_date'] = df['roll_max_date'].fillna(method='ffill')

        df['neckline'] = np.where(df['sell'], df['rolling_max'], 0)

        # convert neckline to list

        neck_list = df['neckline'].tolist()

        neck_list = [i for i in neck_list if i != 0]

        # https://stackoverflow.com/questions/60903774/python-last-number-repeat-more-than-once?rq=1

        neck_list.append(neck_list[-1])

        # print(neck_list)

        df['neck_date'] = np.where(df['neckline'], df['roll_max_date'], 0)

        # https://stackoverflow.com/questions/36684013/extract-column-value-based-on-another-column-pandas-dataframe?rq=1

        neck_date_list = df['neck_date'].tolist()

        neck_date_list = [i for i in neck_date_list if i != 0]

        neck_date_list.append(df['Date'].iloc[-1])

        # print(neck_date_list)

        total_runs = int(len(neck_date_list))

        # convert 2 columns into a dictionary

        # https://cmdlinetips.com/2021/04/convert-two-column-values-from-pandas-dataframe-to-a-dictionary/

        # https://stackoverflow.com/questions/66311549/how-do-i-loop-over-multiple-figures-in-plotly

        # https://stackoverflow.com/questions/60926439/plotly-add-traces-using-a-loop

        # https://stackoverflow.com/questions/58493254/how-to-add-more-than-one-shape-with-loop-in-plotly

        # print(df)

        # df.to_csv('switch.csv')

        # fig = px.scatter(x=neck_date_list, y=neck_list)
        # fig.show()

        fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                              open=df['Open'],
                                              high=df['High'],
                                              low=df['Low'],
                                              close=df['Close'])]

                         )

        for i in range(0, total_runs - 1):
            fig1.add_shape(type="line",
                           x0=neck_date_list[i], y0=neck_list[i], x1=neck_date_list[i + 1], y1=neck_list[i],
                           line=dict(
                               color="LightSeaGreen",
                               width=2,
                           ),
                           )

        fig1.update_layout(hovermode='x', spikedistance=-1, width=1800, height=1200, title=ticker)

        fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                          ticks='inside')

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('notdash.html', graphJSON=graphJSON)
    return render_template('ticker.html')

@application.route('/dropdown', methods=['GET', 'POST'])
def drop_down():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
        ticker = str(symbol)
        # ticker = yf.Ticker(symbol)

        # ticker = "TQQQ"

        # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
        period = details['period']
        interval = details['interval']
        data = yf.download(tickers=ticker, period=period, interval=interval)

        df = pd.DataFrame(data)

        df = df.reset_index()

        df['Date'] = df['Date'].astype(str)

        # print(df)

        df['WMA'] = TA.WMA(df, 9)

        # print(df)

        # Calculate the difference between rows

        # https://www.codeforests.com/2020/10/04/calculate-date-difference-between-rows/

        df['WMA_diff'] = df['WMA'].diff()

        # print(df)

        # https://stackoverflow.com/questions/32984462/setting-1-or-0-to-new-pandas-column-conditionally
        # 1 or 0 switch

        df['slope'] = df['WMA_diff'] > 0

        # print(df)

        df['slope'] = df['slope'].astype(int)

        # print(df)

        # https://newbedev.com/comparing-previous-row-values-in-pandas-dataframe

        df['trigger'] = df['slope'].eq(df['slope'].shift())

        df['trigger'] = df['trigger'].astype(int)

        df['neckline_trigger'] = (df['trigger'] == 0) & (df['slope'] > 0)

        df['neckline_trigger'] = df['neckline_trigger'].astype(int)

        # df['rolling_min'] = df['Low'].rolling(window=3).min().shift(1).fillna(0)

        df['rolling_min'] = df['Low'].rolling(window=4).min().fillna(0)

        df['vertex'] = np.where(df['neckline_trigger'], df['rolling_min'], 0)

        df['sell'] = (df['trigger'] == 0) & (df['slope'] == 0)

        df['sell'] = df['sell'].astype(int)

        # df['rolling_max'] = df['High'].rolling(window=3).max().shift(1).fillna(0)

        df['rolling_max'] = df['High'].rolling(window=4).max().fillna(0)

        df['roll_max_trigger'] = df['rolling_max'].eq(df['rolling_max'].shift())

        df['roll_max_trigger'] = df['roll_max_trigger'].astype(int)

        df['roll_max_date_bool'] = (df['roll_max_trigger'] == 0)

        df['roll_max_date'] = df['Date'].where(df['roll_max_date_bool'])

        df['roll_max_date'] = df['roll_max_date'].fillna(method='ffill')

        df['neckline'] = np.where(df['sell'], df['rolling_max'], 0)

        # convert neckline to list

        neck_list = df['neckline'].tolist()

        neck_list = [i for i in neck_list if i != 0]

        # https://stackoverflow.com/questions/60903774/python-last-number-repeat-more-than-once?rq=1

        neck_list.append(neck_list[-1])

        # print(neck_list)

        df['neck_date'] = np.where(df['neckline'], df['roll_max_date'], 0)

        # https://stackoverflow.com/questions/36684013/extract-column-value-based-on-another-column-pandas-dataframe?rq=1

        neck_date_list = df['neck_date'].tolist()

        neck_date_list = [i for i in neck_date_list if i != 0]

        neck_date_list.append(df['Date'].iloc[-1])

        # print(neck_date_list)

        total_runs = int(len(neck_date_list))

        # convert 2 columns into a dictionary

        # https://cmdlinetips.com/2021/04/convert-two-column-values-from-pandas-dataframe-to-a-dictionary/

        # https://stackoverflow.com/questions/66311549/how-do-i-loop-over-multiple-figures-in-plotly

        # https://stackoverflow.com/questions/60926439/plotly-add-traces-using-a-loop

        # https://stackoverflow.com/questions/58493254/how-to-add-more-than-one-shape-with-loop-in-plotly

        # print(df)

        # df.to_csv('switch.csv')

        # fig = px.scatter(x=neck_date_list, y=neck_list)
        # fig.show()

        fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                              open=df['Open'],
                                              high=df['High'],
                                              low=df['Low'],
                                              close=df['Close'])]

                         )

        for i in range(0, total_runs - 1):
            fig1.add_shape(type="line",
                           x0=neck_date_list[i], y0=neck_list[i], x1=neck_date_list[i + 1], y1=neck_list[i],
                           line=dict(
                               color="LightSeaGreen",
                               width=2,
                           ),
                           )

        fig1.update_layout(hovermode='x', spikedistance=-1, width=1800, height=1200, title=ticker)

        fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                          ticks='inside')

        annote = "{:.2f}".format(float(neck_list[-1]))
        fig1.add_annotation(x=neck_date_list[-2], y=neck_list[-1],
                            text=annote,
                            showarrow=True,
                            arrowhead=1)

        annote1 = "{:.2f}".format(float(neck_list[-3]))
        fig1.add_annotation(x=neck_date_list[-3], y=neck_list[-3],
                            text=annote1,
                            showarrow=True,
                            arrowhead=1)

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('dropdown.html')

@application.route('/vertex', methods=['GET', 'POST'])
def ver_tex():
    if request.method == "POST":
        details = request.form
        symbol = details['ticker']
        ticker = str(symbol)
        # ticker = yf.Ticker(symbol)

        # ticker = "TQQQ"

        # data = yf.download(tickers = ticker, start='2019-01-04', end='2021-06-09')
        period = details['period']
        interval = details['interval']
        data = yf.download(tickers=ticker, period=period, interval=interval)

        df = pd.DataFrame(data)

        df = df.reset_index()

        df['Date'] = df['Date'].astype(str)

        # print(df)

        df['WMA'] = TA.WMA(df, 9)

        # print(df)

        # Calculate the difference between rows

        # https://www.codeforests.com/2020/10/04/calculate-date-difference-between-rows/

        df['WMA_diff'] = df['WMA'].diff()

        # print(df)

        # https://stackoverflow.com/questions/32984462/setting-1-or-0-to-new-pandas-column-conditionally
        # 1 or 0 switch

        df['slope'] = df['WMA_diff'] > 0

        # print(df)

        df['slope'] = df['slope'].astype(int)

        # print(df)

        # https://newbedev.com/comparing-previous-row-values-in-pandas-dataframe

        df['trigger'] = df['slope'].eq(df['slope'].shift())

        df['trigger'] = df['trigger'].astype(int)

        # vertex

        df['rolling_min'] = df['Low'].rolling(window=4).min().fillna(0)

        df['roll_min_trigger'] = df['rolling_min'].eq(df['rolling_min'].shift())

        df['roll_min_trigger'] = df['roll_min_trigger'].astype(int)

        df['roll_min_date_bool'] = (df['roll_min_trigger'] == 0)

        df['roll_min_date'] = df['Date'].where(df['roll_min_date_bool'])

        df['roll_min_date'] = df['roll_min_date'].fillna(method='ffill')

        df['buy'] = (df['trigger'] == 0) & (df['slope'] > 0)

        df['buy'] = df['buy'].astype(int)

        df['vertex'] = np.where(df['buy'], df['rolling_min'], 0)

        # convert vertex to list

        vertex_list = df['vertex'].tolist()

        vertex_list = [i for i in vertex_list if i != 0]

        # # https://stackoverflow.com/questions/60903774/python-last-number-repeat-more-than-once?rq=1

        vertex_list.append(vertex_list[-1])

        # print(vertex_list)

        df['vertex_date'] = np.where(df['vertex'], df['roll_min_date'], 0)

        # # https://stackoverflow.com/questions/36684013/extract-column-value-based-on-another-column-pandas-dataframe?rq=1

        vertex_date_list = df['vertex_date'].tolist()

        vertex_date_list = [i for i in vertex_date_list if i != 0]

        vertex_date_list.append(df['Date'].iloc[-1])

        # print(vertex_date_list)

        # neckline

        df['rolling_max'] = df['High'].rolling(window=4).max().fillna(0)

        df['roll_max_trigger'] = df['rolling_max'].eq(df['rolling_max'].shift())

        df['roll_max_trigger'] = df['roll_max_trigger'].astype(int)

        df['roll_max_date_bool'] = (df['roll_max_trigger'] == 0)

        df['roll_max_date'] = df['Date'].where(df['roll_max_date_bool'])

        df['roll_max_date'] = df['roll_max_date'].fillna(method='ffill')

        df['sell'] = (df['trigger'] == 0) & (df['slope'] == 0)

        df['sell'] = df['sell'].astype(int)

        df['neckline'] = np.where(df['sell'], df['rolling_max'], 0)

        # df.to_csv('vertex.csv')

        # convert neckline to list

        neck_list = df['neckline'].tolist()

        neck_list = [i for i in neck_list if i != 0]

        # https://stackoverflow.com/questions/60903774/python-last-number-repeat-more-than-once?rq=1

        neck_list.append(neck_list[-1])

        print(neck_list)

        df['neck_date'] = np.where(df['neckline'], df['roll_max_date'], 0)

        # https://stackoverflow.com/questions/36684013/extract-column-value-based-on-another-column-pandas-dataframe?rq=1

        neck_date_list = df['neck_date'].tolist()

        neck_date_list = [i for i in neck_date_list if i != 0]

        neck_date_list.append(df['Date'].iloc[-1])

        print(neck_date_list)

        # https://cmdlinetips.com/2021/04/convert-two-column-values-from-pandas-dataframe-to-a-dictionary/

        # https://stackoverflow.com/questions/66311549/how-do-i-loop-over-multiple-figures-in-plotly

        # https://stackoverflow.com/questions/60926439/plotly-add-traces-using-a-loop

        # https://stackoverflow.com/questions/58493254/how-to-add-more-than-one-shape-with-loop-in-plotly

        fig1 = go.Figure(data=[go.Candlestick(x=df['Date'],
                                              open=df['Open'],
                                              high=df['High'],
                                              low=df['Low'],
                                              close=df['Close'])]

                         )

        total_runs = int(len(neck_date_list))

        for i in range(0, total_runs - 1):
            fig1.add_shape(type="line",
                           x0=neck_date_list[i], y0=neck_list[i], x1=neck_date_list[i + 1], y1=neck_list[i],
                           line=dict(
                               color="LightSeaGreen",
                               width=2,
                           ),
                           )

        total_vertex_runs = int(len(vertex_date_list))

        for j in range(0, total_vertex_runs - 1):
            fig1.add_shape(type="line",
                           x0=vertex_date_list[j], y0=vertex_list[j], x1=vertex_date_list[j + 1], y1=vertex_list[j],
                           line=dict(
                               color="darkred",
                               width=2,
                           ),
                           )

        annote = "{:.2f}".format(float(neck_list[-1]))

        fig1.add_annotation(x=neck_date_list[-2], y=neck_list[-1],
                            text=annote,
                            showarrow=True,
                            arrowhead=1)

        annote1 = "{:.2f}".format(float(neck_list[-3]))

        fig1.add_annotation(x=neck_date_list[-3], y=neck_list[-3],
                            text=annote1,
                            showarrow=True,
                            arrowhead=1)

        fig1.update_layout(dict(hovermode='x'), spikedistance=-1, width=1800, height=1200, title=ticker)

        fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                          ticks='inside')

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('dropdown.html')

@application.route('/targets', methods=['GET', 'POST'])
def tar_gets():
    if request.method == "POST":

        details = request.form

        symbol = details['ticker']
        ticker = str(symbol)
        # period = details['period']
        # interval = int(details['periodschange'])

        data = yf.download(tickers=ticker, period='2y', interval='1d')

        df1 = pd.DataFrame(data)

        # print(df1)

        df = df1.reset_index()

        # print(df)

        df7 = df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                 'Volume': 'volume'}, inplace=False)

        # print(df7)
        # df7.to_csv('daily.csv')

        n = 5

        df3 = df7.groupby(np.arange(len(df7)) // n).max()  # high
        # print('df3 max:', df3)

        df4 = df7.groupby(np.arange(len(df7)) // n).min()  # low
        # print('df4 min:', df4)

        df5 = df7.groupby(np.arange(len(df7)) // n).first()  # open
        # print('df5 open:', df5)

        df6 = df7.groupby(np.arange(len(df7)) // n).last()  # close
        # print('df6 close:', df6)

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        # print(agg_df)

        df2 = agg_df

        print(df2)
        num_periods = 21
        df2['SMA'] = TA.SMA(df2, 21)
        df2['FRAMA'] = TA.FRAMA(df2, 10)
        df2['TEMA'] = TA.TEMA(df2, num_periods)
        # df2['VWAP'] = TA.VWAP(df2)

        # how to get previous row's value
        # df2['previous'] = df2['lower_band'].shift(1)

        # # how to get the power of another column
        df2['test'] = 5
        # df2['square'] = df2['test'].pow(2)
        # df2['square'] = df2['test']**2

        # recursive
        df2.loc[0, 'diff'] = df2.loc[0, 'test'] * 0.4
        df2.loc[1, 'diff'] = df2.loc[1, 'test'] * 0.4
        df2.loc[2, 'diff'] = df2.loc[2, 'test'] * 0.4
        df2.loc[3, 'diff'] = df2.loc[3, 'test'] * 0.4

        for i in range(4, len(df2)):
            df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i - 1, 'diff'] + df2.loc[i - 2, 'diff']

        # for i in range(1, len(df2)):
        #     df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i-1, 'diff']

        # pi
        # df2['pi'] = math.pi

        # cosine
        # df2['cos'] = np.cos(df2['test'])

        # Gauss
        num_periods_gauss = 15.5
        df2['symbol'] = 2 * math.pi / num_periods_gauss
        df2['beta'] = (1 - np.cos(df2['symbol'])) / ((1.414) ** (0.5) - 1)
        df2['alpha'] = - df2['beta'] + (df2['beta'] ** 2 + df2['beta'] * 2) ** 2

        # Gauss equation
        # initialize
        df2.loc[0, 'gauss'] = df2.loc[0, 'close']
        df2.loc[1, 'gauss'] = df2.loc[1, 'close']
        df2.loc[2, 'gauss'] = df2.loc[2, 'close']
        df2.loc[3, 'gauss'] = df2.loc[3, 'close']
        df2.loc[4, 'gauss'] = df2.loc[4, 'close']

        for i in range(4, len(df2)):
            df2.loc[i, 'gauss'] = df2.loc[i, 'close'] * df2.loc[i, 'alpha'] ** 4 + (4 * (1 - df2.loc[i, 'alpha'])) * \
                                  df2.loc[i - 1, 'gauss'] \
                                  - (6 * ((1 - df2.loc[i, 'alpha']) ** 2) * df2.loc[i - 2, 'gauss']) \
                                  + (4 * (1 - df2.loc[i, 'alpha']) ** 3) * df2.loc[i - 3, 'gauss'] \
                                  - ((1 - df2.loc[i, 'alpha']) ** 4) * df2.loc[i - 4, 'gauss']

        # ATR

        # https://www.statology.org/exponential-moving-average-pandas/
        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
        # df2['ATR'] = df2['ATR_diff'].rolling(window=num_periods_ATR).mean()
        df2['Line'] = df2['gauss']
        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 1.4

        df2['upper_band_1'] = df2['Line'] + multiplier_1 * df2['ATR']
        df2['lower_band_1'] = df2['Line'] - multiplier_1 * df2['ATR']

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR']
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR']

        # print(df2)

        # df2.to_csv("gauss.csv")

        # https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

        # https://plotly.com/python/legend/#legend-item-names

        # fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'])]

                         )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band'],
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band'],
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band_1'],
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band_1'],
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['Line'],
                name="Gauss",
                mode="lines",
                line=go.scatter.Line(color="blue"),
                showlegend=True)
        )

        fig1.update_layout(dict(hovermode='x'), spikedistance=-1, width=1800, height=1200, title=ticker)

        fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                          ticks='inside')

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('ticker.html')

@application.route('/targetsdropdown', methods=['GET', 'POST'])
def targets_dropdown():
    if request.method == "POST":

        details = request.form

        symbol = details['ticker']
        ticker = str(symbol)
        period = details['period']
        interval = int(details['interval'])

        data = yf.download(tickers=ticker, period=period, interval='1d')

        df1 = pd.DataFrame(data)

        # print(df1)

        df = df1.reset_index()

        # print(df)

        df7 = df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                 'Volume': 'volume'}, inplace=False)

        # print(df7)
        # df7.to_csv('daily.csv')

        n = interval

        df3 = df7.groupby(np.arange(len(df7)) // n).max()  # high
        # print('df3 max:', df3)

        df4 = df7.groupby(np.arange(len(df7)) // n).min()  # low
        # print('df4 min:', df4)

        df5 = df7.groupby(np.arange(len(df7)) // n).first()  # open
        # print('df5 open:', df5)

        df6 = df7.groupby(np.arange(len(df7)) // n).last()  # close
        # print('df6 close:', df6)

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        # print(agg_df)

        df2 = agg_df

        print(df2)
        num_periods = 21
        df2['SMA'] = TA.SMA(df2, 21)
        df2['FRAMA'] = TA.FRAMA(df2, 10)
        df2['TEMA'] = TA.TEMA(df2, num_periods)
        # df2['VWAP'] = TA.VWAP(df2)

        # how to get previous row's value
        # df2['previous'] = df2['lower_band'].shift(1)

        # # how to get the power of another column
        df2['test'] = 5
        # df2['square'] = df2['test'].pow(2)
        # df2['square'] = df2['test']**2

        # recursive
        df2.loc[0, 'diff'] = df2.loc[0, 'test'] * 0.4
        df2.loc[1, 'diff'] = df2.loc[1, 'test'] * 0.4
        df2.loc[2, 'diff'] = df2.loc[2, 'test'] * 0.4
        df2.loc[3, 'diff'] = df2.loc[3, 'test'] * 0.4

        for i in range(4, len(df2)):
            df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i - 1, 'diff'] + df2.loc[i - 2, 'diff']

        # for i in range(1, len(df2)):
        #     df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i-1, 'diff']

        # pi
        # df2['pi'] = math.pi

        # cosine
        # df2['cos'] = np.cos(df2['test'])

        # Gauss
        num_periods_gauss = 15.5
        df2['symbol'] = 2 * math.pi / num_periods_gauss
        df2['beta'] = (1 - np.cos(df2['symbol'])) / ((1.414) ** (0.5) - 1)
        df2['alpha'] = - df2['beta'] + (df2['beta'] ** 2 + df2['beta'] * 2) ** 2

        # Gauss equation
        # initialize
        df2.loc[0, 'gauss'] = df2.loc[0, 'close']
        df2.loc[1, 'gauss'] = df2.loc[1, 'close']
        df2.loc[2, 'gauss'] = df2.loc[2, 'close']
        df2.loc[3, 'gauss'] = df2.loc[3, 'close']
        df2.loc[4, 'gauss'] = df2.loc[4, 'close']

        for i in range(4, len(df2)):
            df2.loc[i, 'gauss'] = df2.loc[i, 'close'] * df2.loc[i, 'alpha'] ** 4 + (4 * (1 - df2.loc[i, 'alpha'])) * \
                                  df2.loc[i - 1, 'gauss'] \
                                  - (6 * ((1 - df2.loc[i, 'alpha']) ** 2) * df2.loc[i - 2, 'gauss']) \
                                  + (4 * (1 - df2.loc[i, 'alpha']) ** 3) * df2.loc[i - 3, 'gauss'] \
                                  - ((1 - df2.loc[i, 'alpha']) ** 4) * df2.loc[i - 4, 'gauss']

        # ATR

        # https://www.statology.org/exponential-moving-average-pandas/
        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
        # df2['ATR'] = df2['ATR_diff'].rolling(window=num_periods_ATR).mean()
        df2['Line'] = df2['gauss']
        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 1.4

        df2['upper_band_1'] = df2['Line'] + multiplier_1 * df2['ATR']
        df2['lower_band_1'] = df2['Line'] - multiplier_1 * df2['ATR']

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR']
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR']

        # print(df2)

        # df2.to_csv("gauss.csv")

        # https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

        # https://plotly.com/python/legend/#legend-item-names

        # fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'])]

                         )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band'],
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band'],
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band_1'],
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band_1'],
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['Line'],
                name="Gauss",
                mode="lines",
                line=go.scatter.Line(color="blue"),
                showlegend=True)
        )

        fig1.update_layout(dict(hovermode='x'), spikedistance=-1, width=1800, height=1200, title=ticker)

        fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                          ticks='inside')

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('gauss.html')

@application.route('/targetdates', methods=['GET', 'POST'])
def target_dates():
    if request.method == "POST":

        details = request.form

        symbol = details['ticker']
        ticker = str(symbol)
        # period = details['period']
        interval = int(details['interval'])
        start_date = str(details['start_date'])
        end_date = str(details['end_date'])

        data = yf.download(tickers = ticker, start=start_date, end=end_date)
        # data = yf.download(tickers=ticker, period='2y', interval='1d')

        df1 = pd.DataFrame(data)

        # print(df1)

        df = df1.reset_index()

        # print(df)

        df7 = df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                 'Volume': 'volume'}, inplace=False)

        # print(df7)
        # df7.to_csv('daily.csv')

        n = interval

        df3 = df7.groupby(np.arange(len(df7)) // n).max()  # high
        # print('df3 max:', df3)

        df4 = df7.groupby(np.arange(len(df7)) // n).min()  # low
        # print('df4 min:', df4)

        df5 = df7.groupby(np.arange(len(df7)) // n).first()  # open
        # print('df5 open:', df5)

        df6 = df7.groupby(np.arange(len(df7)) // n).last()  # close
        # print('df6 close:', df6)

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        # print(agg_df)

        df2 = agg_df

        # print(df2)
        num_periods = 21
        df2['SMA'] = TA.SMA(df2, 21)
        df2['FRAMA'] = TA.FRAMA(df2, 10)
        df2['TEMA'] = TA.TEMA(df2, num_periods)
        # df2['VWAP'] = TA.VWAP(df2)

        # how to get previous row's value
        # df2['previous'] = df2['lower_band'].shift(1)

        # # how to get the power of another column
        df2['test'] = 5
        # df2['square'] = df2['test'].pow(2)
        # df2['square'] = df2['test']**2

        # recursive
        df2.loc[0, 'diff'] = df2.loc[0, 'test'] * 0.4
        df2.loc[1, 'diff'] = df2.loc[1, 'test'] * 0.4
        df2.loc[2, 'diff'] = df2.loc[2, 'test'] * 0.4
        df2.loc[3, 'diff'] = df2.loc[3, 'test'] * 0.4

        for i in range(4, len(df2)):
            df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i - 1, 'diff'] + df2.loc[i - 2, 'diff']

        # for i in range(1, len(df2)):
        #     df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i-1, 'diff']

        # pi
        # df2['pi'] = math.pi

        # cosine
        # df2['cos'] = np.cos(df2['test'])

        # Gauss
        num_periods_gauss = 15.5
        df2['symbol'] = 2 * math.pi / num_periods_gauss
        df2['beta'] = (1 - np.cos(df2['symbol'])) / ((1.414) ** (0.5) - 1)
        df2['alpha'] = - df2['beta'] + (df2['beta'] ** 2 + df2['beta'] * 2) ** 2

        # Gauss equation
        # initialize
        df2.loc[0, 'gauss'] = df2.loc[0, 'close']
        df2.loc[1, 'gauss'] = df2.loc[1, 'close']
        df2.loc[2, 'gauss'] = df2.loc[2, 'close']
        df2.loc[3, 'gauss'] = df2.loc[3, 'close']
        df2.loc[4, 'gauss'] = df2.loc[4, 'close']

        for i in range(4, len(df2)):
            df2.loc[i, 'gauss'] = df2.loc[i, 'close'] * df2.loc[i, 'alpha'] ** 4 + (4 * (1 - df2.loc[i, 'alpha'])) * \
                                  df2.loc[i - 1, 'gauss'] \
                                  - (6 * ((1 - df2.loc[i, 'alpha']) ** 2) * df2.loc[i - 2, 'gauss']) \
                                  + (4 * (1 - df2.loc[i, 'alpha']) ** 3) * df2.loc[i - 3, 'gauss'] \
                                  - ((1 - df2.loc[i, 'alpha']) ** 4) * df2.loc[i - 4, 'gauss']

        # ATR

        # https://www.statology.org/exponential-moving-average-pandas/
        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
        # df2['ATR'] = df2['ATR_diff'].rolling(window=num_periods_ATR).mean()
        df2['Line'] = df2['gauss']
        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 1.4

        df2['upper_band_1'] = df2['Line'] + multiplier_1 * df2['ATR']
        df2['lower_band_1'] = df2['Line'] - multiplier_1 * df2['ATR']

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR']
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR']

        # print(df2)

        # df2.to_csv("gauss.csv")

        # https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

        # https://plotly.com/python/legend/#legend-item-names

        # fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'])]

                         )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band'],
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band'],
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band_1'],
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band_1'],
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['Line'],
                name="Gauss",
                mode="lines",
                line=go.scatter.Line(color="blue"),
                showlegend=True)
        )

        fig1.update_layout(dict(hovermode='x'), spikedistance=-1, width=1800, height=1200, title=ticker)

        fig1.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True, showgrid=True,
                          ticks='inside')

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('datesinervals.html')

@application.route('/atr', methods=['GET', 'POST'])
def atr_dates():
    if request.method == "POST":

        details = request.form

        symbol = details['ticker']
        ticker = str(symbol)

        start_date = str(details['start_date'])
        end_date = str(details['end_date'])

        # start_date = '2020-01-04'
        # end_date = '2021-12-10'
        # data = yf.download(tickers=ticker, start=start_date, end=end_date)

        # data = yf.download(tickers=ticker, start='2020-01-04', end='2021-12-10')
        data = yf.download(tickers = ticker, period = "2y")

        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo

        df1 = pd.DataFrame(data)

        df = df1.reset_index()

        df7 = df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                 'Volume': 'volume'}, inplace=False)

        # print(df7)
        # df7.to_csv('daily.csv')

        # interval = int(details['interval'])
        n = 5

        df3 = df7.groupby(np.arange(len(df7)) // n).max()  # high

        df4 = df7.groupby(np.arange(len(df7)) // n).min()  # low

        df5 = df7.groupby(np.arange(len(df7)) // n).first()  # open

        df6 = df7.groupby(np.arange(len(df7)) // n).last()  # close

        agg_df = pd.DataFrame()

        agg_df['date'] = df6['date']
        agg_df['low'] = df4['low']
        agg_df['high'] = df3['high']
        agg_df['open'] = df5['open']
        agg_df['close'] = df6['close']

        df2 = agg_df

        # print(df2)
        num_periods = 21
        df2['SMA'] = TA.SMA(df2, 21)
        df2['FRAMA'] = TA.FRAMA(df2, 10)
        df2['TEMA'] = TA.TEMA(df2, num_periods)
        # df2['VWAP'] = TA.VWAP(df2)

        # how to get previous row's value
        # df2['previous'] = df2['lower_band'].shift(1)

        # recursive
        df2['test'] = 5
        df2.loc[0, 'diff'] = df2.loc[0, 'test'] * 0.4
        df2.loc[1, 'diff'] = df2.loc[1, 'test'] * 0.4
        df2.loc[2, 'diff'] = df2.loc[2, 'test'] * 0.4
        df2.loc[3, 'diff'] = df2.loc[3, 'test'] * 0.4

        for i in range(4, len(df2)):
            df2.loc[i, 'diff'] = df2.loc[i, 'test'] + df2.loc[i - 1, 'diff'] + df2.loc[i - 2, 'diff']

        # Gauss
        num_periods_gauss = 15.5
        df2['symbol'] = 2 * math.pi / num_periods_gauss
        df2['beta'] = (1 - np.cos(df2['symbol'])) / ((1.414) ** (0.5) - 1)
        df2['alpha'] = - df2['beta'] + (df2['beta'] ** 2 + df2['beta'] * 2) ** 2

        # Gauss equation
        # initialize
        df2.loc[0, 'gauss'] = df2.loc[0, 'close']
        df2.loc[1, 'gauss'] = df2.loc[1, 'close']
        df2.loc[2, 'gauss'] = df2.loc[2, 'close']
        df2.loc[3, 'gauss'] = df2.loc[3, 'close']
        df2.loc[4, 'gauss'] = df2.loc[4, 'close']

        for i in range(4, len(df2)):
            df2.loc[i, 'gauss'] = df2.loc[i, 'close'] * df2.loc[i, 'alpha'] ** 4 + (4 * (1 - df2.loc[i, 'alpha'])) * \
                                  df2.loc[i - 1, 'gauss'] \
                                  - (6 * ((1 - df2.loc[i, 'alpha']) ** 2) * df2.loc[i - 2, 'gauss']) \
                                  + (4 * (1 - df2.loc[i, 'alpha']) ** 3) * df2.loc[i - 3, 'gauss'] \
                                  - ((1 - df2.loc[i, 'alpha']) ** 4) * df2.loc[i - 4, 'gauss']

        # ATR
        num_periods_ATR = 21
        multiplier = 1

        df2['ATR_diff'] = df2['high'] - df2['low']
        df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()

        df2['Line'] = df2['gauss']

        # upper bands and ATR

        df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
        df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

        multiplier_1 = 1.6
        multiplier_2 = 2.3

        df2['upper_band_1'] = df2['Line'] + multiplier_1 * df2['ATR']
        df2['lower_band_1'] = df2['Line'] - multiplier_1 * df2['ATR']

        df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR']
        df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR']

        # forecasting begins

        # df2['line_change'] = df2['Line'] - df2['Line'].shift(1)
        df2['line_change'] = df2['Line'] - df2['Line'].shift(1)
        df3 = pd.DataFrame()
        df3['date'] = df2['date']
        df3['close'] = df2['line_change']
        df3['open'] = df2['line_change']
        df3['high'] = df2['line_change']
        df3['low'] = df2['line_change']

        # calculate dates from which to calculate slope
        # slope_begin_date = str(details['slope_begin_dt'])
        # slope_end_date = str(details['slope_end_dt'])
        slope_begin_date = start_date
        slope_end_date = end_date
        slope_begin_date_index = df3[df3['date'] == slope_begin_date].index.values.astype(int)[0]
        slope_end_date_index = df3[df3['date'] == slope_end_date].index.values.astype(int)[0]
        # print(slope_begin_date_index)
        # print(slope_end_date_index)
        slope_bars = slope_end_date_index - slope_begin_date_index
        # print(slope_bars)
        slope_periods_change = int(slope_bars)  # drives the projection by choosing number of periods back

        # calculate slope
        df3['change_SMA'] = TA.SMA(df3, slope_periods_change)  # drives the projection

        df3.to_csv('sma_change.csv')

        slope = df3['change_SMA'].iloc[slope_end_date_index]
        # print(slope)

        # calculate atr
        df4 = pd.DataFrame()
        df4['date'] = df2['date']
        df4['close'] = df2['ATR']
        df4['open'] = df2['ATR']
        df4['high'] = df2['ATR']
        df4['low'] = df2['ATR']

        # atr_begin_date = str(details['atr_begin_dt'])
        # atr_end_date = str(details['atr_end_dt'])
        atr_begin_date = slope_begin_date
        atr_end_date = slope_end_date
        atr_begin_date_index = df4[df4['date'] == atr_begin_date].index.values.astype(int)[0]
        atr_end_date_index = df4[df4['date'] == atr_end_date].index.values.astype(int)[0]
        atr_bars = atr_end_date_index - atr_begin_date_index

        atr_periods_change = int(atr_bars)

        df4['forecasted_ATR'] = TA.SMA(df4, atr_periods_change)
        # df4.to_csv('forecasted_ATR.csv')

        ATR = df4['forecasted_ATR'].iloc[atr_end_date_index]
        # print(ATR)

        # try the loop again

        date_diff = df2.loc[len(df2) - 1, 'date'] - df2.loc[len(df2) - 2, 'date']

        # line_diff = df2.loc[len(df2)-1, 'change_SMA']

        line_diff = slope

        # https://stackoverflow.com/questions/12691551/add-n-business-days-to-a-given-date-ignoring-holidays-and-weekends-in-python

        def date_by_adding_business_days(from_date, add_days):
            business_days_to_add = add_days
            current_date = from_date
            while business_days_to_add > 0:
                current_date += timedelta(days=1)
                weekday = current_date.weekday()
                if weekday >= 5:  # sunday = 6
                    continue
                business_days_to_add -= 1
            return current_date

        counter = 0
        bars_out = 20
        while counter < bars_out:
            df2.loc[len(df2), 'Line'] = df2.loc[len(df2) - 1, 'Line'] + line_diff
            df2.loc[len(df2) - 1, 'date'] = date_by_adding_business_days(df2.loc[len(df2) - 2, 'date'], n)
            counter += 1

        ATR = ATR * multiplier
        ATR_1 = ATR * multiplier_1
        ATR_2 = ATR * multiplier_2

        counter1 = 0
        while counter1 < bars_out:
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_1'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR_1
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_1'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR_1
            # df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band_2'] = df2.loc[len(
            #     df2) - bars_out - 1 + counter1, 'Line'] + ATR_2
            # df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band_2'] = df2.loc[len(
            #     df2) - bars_out - 1 + counter1, 'Line'] - ATR_2
            df2.loc[len(df2) - bars_out + counter1 - 1, 'upper_band'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] + ATR
            df2.loc[len(df2) - bars_out + counter1 - 1, 'lower_band'] = df2.loc[len(
                df2) - bars_out - 1 + counter1, 'Line'] - ATR

            counter1 += 1

        # append dataframe
        # https://stackoverflow.com/questions/53304656/difference-between-dates-between-corresponding-rows-in-pandas-dataframe
        # https://www.geeksforgeeks.org/how-to-add-one-row-in-an-existing-pandas-dataframe/
        # https://stackoverflow.com/questions/10715965/create-pandas-dataframe-by-appending-one-row-at-a-time
        # https://stackoverflow.com/questions/49916371/how-to-append-new-row-to-dataframe-in-pandas
        # https://stackoverflow.com/questions/50607119/adding-a-new-row-to-a-dataframe-why-loclendf-instead-of-iloclendf
        # https://stackoverflow.com/questions/31674557/how-to-append-rows-in-a-pandas-dataframe-in-a-for-loop

        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                              open=df2['open'],
                                              high=df2['high'],
                                              low=df2['low'],
                                              close=df2['close'], showlegend=True)]

                         )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band'].round(2),
                name='upper band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band'].round(2),
                name='lower band',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['upper_band_1'].round(2),
                name='upper band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['lower_band_1'].round(2),
                name='lower band_1',
                mode="lines",
                line=go.scatter.Line(color="gray"),
                showlegend=True)
        )

        # fig1.add_trace(
        #     go.Scatter(
        #         x=df2['date'],
        #         y=df2['upper_band_2'].round(2),
        #         name='upper band_2',
        #         mode="lines",
        #         line=go.scatter.Line(color="gray"),
        #         showlegend=True)
        # )
        #
        # fig1.add_trace(
        #     go.Scatter(
        #         x=df2['date'],
        #         y=df2['lower_band_2'].round(2),
        #         name='lower band_2',
        #         mode="lines",
        #         line=go.scatter.Line(color="gray"),
        #         showlegend=True)
        # )

        fig1.add_trace(
            go.Scatter(
                x=df2['date'],
                y=df2['Line'].round(2),
                name="WMA",
                mode="lines",
                line=go.scatter.Line(color="blue"),
                showlegend=True)
        )

        fig1.update_layout(
            title=ticker, width=1800, height=1200, hovermode='x unified'
        )

        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('neckline.html', graphJSON=graphJSON)
    return render_template('dates.html')
