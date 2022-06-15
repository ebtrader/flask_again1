import yfinance as yf
import pandas as pd

# @application.route('/calculatorupro', methods=['GET', 'POST'])
# def upro_target():
#     if request.method == "POST":
#         details = request.form

# target = details['ticker']
# target = int(target)
target = 32.70
ticker_input = "FAS"

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
    print(df)

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
    print(df)

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
    print(df)

else:
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
    print(df)

# return df.to_html(header='true', table_id='table')
# return render_template('target.html')
