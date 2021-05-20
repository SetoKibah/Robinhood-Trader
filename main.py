import config
import robin_stocks as rh
import datetime as dt
import time
import os
import pyotp

totp = pyotp.TOTP("My2factorAppHere").now()
print('Current OTP: ', totp)

# Login function
def login():
    totp = pyotp.TOTP("My2factorAppHere").now()
    rh.login(os.environ['USERNAME'], os.environ['PASSWORD'], mfa_code = totp)

# Logout function
def logout():
    rh.logout()


def get_stocks():
    stocks = list()
    stocks.append('INPX')
    stocks.append('HHT')
    stocks.append('CNET')
    return(stocks)


def open_market():
    market = False
    time_now = dt.datetime.now().time

    market_open = dt.time(7,00,0) # 7:00 am
    market_close = dt.time(13, 59, 0) # 1:59 pm

    if time_now > market_open and time_now < market_close:
        market = True
    else:
        print('### Market is closed.')

    return(market)


if __name__ == "__main__":
    
    login()
    
    stocks = get_stocks
    print('Stocks: ', stocks)

    while open_market():
        prices = rh.stocks.get_latest_prices(stocks)
        print('prices:', prices)

        time.sleep(10)