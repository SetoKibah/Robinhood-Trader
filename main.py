import config
import trade_strat
import os
import robin_stocks as rh
import datetime as dt
import time
import pyotp
# This will login as of 09-25-2021
# Video modifying https://www.youtube.com/watch?v=-JTkNoIayR0

totp = pyotp.TOTP(os.environ["AUTH_APP"]).now()
print('Current OTP: ', totp)

# Login function


def login(days):
    time_logged_in = 60*60*24*days
    rh.robinhood.authentication.login(os.environ['USERNAME'],
                            password=os.environ['PASSWORD'],
                            expiresIn = time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)

# Logout function
def logout():
    rh.robinhood.logout()


def get_stocks():
    stocks = list()
    stocks.append('NOK')
    stocks.append('PLTR')
    stocks.append('SOFI')
    stocks.append('F')
    return(stocks)


def open_market():
    market = False
    time_now = dt.datetime.now().time()
    

    market_open = dt.time(13,30,0) # 7:30 am
    market_close = dt.time(19,59,0) # 1:59 pm

    if time_now > market_open and time_now < market_close:
        market = True
        
    else:
      #print('### Market is closed.')
      pass

    return(market)


if __name__ == "__main__":
    
    login(days=1)

    stocks = get_stocks()
    print('Stocks: ', stocks)
    
    ts = trade_strat.Trader(stocks)
    

    while open_market():
        prices = rh.robinhood.stocks.get_latest_price(stocks)
        

        for i, stock in enumerate(stocks):
            price = float(prices[i])
            print('{} = ${}'.format(stock, price))
            
            df_prices = ts.get_historical_prices(stock, span='day')
            sma = ts.get_sma(stock, df_prices, window=12)
            p_sma = ts.get_price_sma(price, sma)
            print('p_sma:', p_sma)
            trade = ts.trade_option(stock, price)
            print('trade: ', trade)

        time.sleep(30)

    logout()