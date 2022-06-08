import pandas as pd
import robin_stocks.robinhood as rh

class Trader():
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.run_time = 0
        self.buffer = 0.04

        self.price_sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

        #print('price_sma_hour:', self.price_sma_hour)
    
    def get_historical_prices(self, stock, span):
        span_interval = {'day': '5minute', 'week': '10minute', 'month': 'hour', '3month': 'hour', 'year': 'day', '5year': 'week'}
        interval = span_interval[span]

        historical_data = rh.stocks.get_stock_historicals(stock, interval=interval, span=span, bounds='regular')
        
        df = pd.DataFrame(historical_data)

        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        close_prices = df.loc[:, 'close_price'].astype('float')

        df_price = pd.concat([close_prices, dates_times], axis=1)
        df_price = df_price.rename(columns={'close_price': stock})
        df_price = df_price.set_index('begins_at')

        return(df_price)

    def get_sma(self, stock, df_prices, window=12):
        sma = df_prices.rolling(window=window, min_periods=window).mean()
        sma = round(float(sma[stock].iloc[-1]), 4)
        return(sma)
    
    def get_price_sma(self, price, sma):
        price_sma = round(price/sma, 4)
        return(price_sma)
    
    def trade_option(self, stock, price):
        # get new sma_hour every 5 minutes
        if self.run_time % (300/60) == 0:
            df_historical_prices = self.get_historical_prices(stock, span='month')
            self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-12:], window=12)
        
        self.price_sma_hour[stock] = self.get_price_sma(price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]

        i1 = "BUY" if p_sma<(1.0 - self.buffer) else "SELL" if p_sma>(1.0 + self.buffer) else "NONE"
        if i1 == "BUY":
            trade = "BUY"
        elif i1 == "SELL":
            trade = "SELL"
        else:
            trade = "HOLD"
        

        return(trade)