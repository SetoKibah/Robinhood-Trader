import config
import robin_stocks as rh
import datetime as dt
import time
import pyotp


totp = pyotp.TOTP("My2factorAppHere").now()
print('Current OTP: ', totp)

# Login function
def login(days):
    time_logged_in = 60*60*24*days
    rh.robinhood.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
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
    stocks.append('VIAC')
    return(stocks)


def open_market():
    market = True
    time_now = dt.datetime.now().time()

    market_open = dt.time(7,00,0) # 7:00 am
    market_close = dt.time(13,59,0) # 1:59 pm

    if time_now > market_open and time_now < market_close:
        market = True
    else:
        print('### Market is closed.')

    return(market)


if __name__ == "__main__":
    
    login(days=1)

    stocks = get_stocks()
    print('Stocks: ', stocks)

    while open_market():
        prices = rh.robinhood.stocks.get_latest_price(stocks)
        print('prices:', prices)

        for i, stock in enumerate(stocks):
            price = float(prices[i])
            print('{} = ${}'.format(stock, price))

        time.sleep(10)

    logout()