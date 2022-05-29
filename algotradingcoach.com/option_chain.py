import yfinance as yf
import pandas as pd

symbol = 'TQQQ'
ticker = yf.Ticker(symbol)
exp_dates = ticker.options
# print(exp_dates)
df = pd.DataFrame()
for x in exp_dates:
    opt = ticker.option_chain(x)
    df = df.append(opt.calls, ignore_index=True)

print(df)
