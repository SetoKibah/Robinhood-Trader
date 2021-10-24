import config
import trade_strat
import os
import random
import robin_stocks.robinhood as rh
import datetime as dt
import time
import pytz
import pyotp
from replit import db

################################################################
# CURRENT SETTING: SMA with week setting and with Daytrading allowable_holdings.
# GOAL: Achieve $400 portfolio value to show that bot is making back losses from testing. Then more money may be allocated to increase profit times.
# Hopeful to be achieved in 3 weeks from 10/14/2021
# Hopeful Target date: 10/29/2021

# TEST WEEK: week of 10/25/2021 - 10/29/2021
# Start and End are based off Market Time

# As a result of a poor end-of-week performance last week, modifier for sell SMA has been increased to 0.01 additional trigger. Intent is to reduce poor sell orders in favor of higher-trend sales. Unlikely to hit target if market fails to deliver.

# Monday Start Value:
# Monday End Value:

# Tuesday Start Value:
# Tuesday End Value:

# Wednesday Start Value:
# Wednesday End Value:

# Thursday Start Value:
# Thursday End Value:
# Friday Start Value:
# Friday End Value:

################################################################

totp = pyotp.TOTP(os.environ["AUTH_APP"]).now()
#print('Current OTP: ', totp)
#time.sleep(30)

# Login function
def login(days):
    time_logged_in = 60*60*24*days
    rh.authentication.login(os.environ['USERNAME'],
                            password=os.environ['PASSWORD'],
                            expiresIn = time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True,
                            mfa_code =totp)

# Logout function
def logout():
    rh.logout()

    current_timezone = pytz.timezone("US/Mountain")
    f = open("log.txt", "a")
    f.write(f"Logout: {dt.datetime.now(current_timezone)}\n")
    f.close()

# Stocks acquisition function
def get_stocks():
    stocks = ['NOK',
              'PLTR',
              'SOFI',
              'F',
              'KR',
              'GPRO',
              'EM',
              'GE',
              'CEI',
              'PFE',
              'ACB',
              'DAL',
              'BB',
              'SBUX',
              'T',
              'TWTR',
              'UBER',
              'GM',
              'CRON',
              'SIRI',
              'SPCE',
              'RBLX',
              'MRO',
              'RIOT',
              'ET',
              'SONY',
              'VZ',
              'INTC',
              'DELL',
              'ATVI',
              'NTDOY',
              'PINS',
              'HPQ',
              'BBY',
              'STX',
              'LOGI',
              'GDDY',
              'DBX',
              'DXC',
              'IMCC',
              'INCR',
              'NVS',
              'TCEHY',
              'ORCL',
              'AZN',
              'CSCO',
              'AVGO',
              'U',
              'EA',
              'PCRFY',
              'HAS',
              'PEP',
              'FCEL',
              'ZNGA',
              'NCLH',
              'DKNG'] # 56 Stocks monitoring as of 10/21/2021
    random.shuffle(stocks)
    return(stocks)

def get_cryptos():
  cryptos = ['BTC', 'DOGE', 'ETH', 'LTC','BSV','BCH','ETC']
  return(cryptos)

# Market hours function
def open_market():
    # Market is set to closed unless conditions are met
    market = False
    time_now = dt.datetime.now().time()

    # Weekday 0-6, 0 is Monday, 6 is Sunday
    weekday = dt.datetime.now().weekday()

    market_open = dt.time(13,30,0) # 7:30 am
    market_close = dt.time(19,59,0) # 1:59 pm

    if time_now > market_open and time_now < market_close and weekday < 5:
        market = True
        
    else:
      print('### Market is closed.')


    return(market)

# Function to cash on account
def get_cash():
    rh_cash = rh.account.build_user_profile()
    
    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    return(cash, equity)

# Function for getting bought prices and holdings
def get_holdings_and_bought_price(stocks):
    holdings = {stocks[i]: 0 for i in range(0, len(stocks))}
    bought_price = {stocks[i]: 0 for i in range(0, len(stocks))}
    rh_holdings = rh.account.build_holdings()

    for stock in stocks:
        try:
            holdings[stock] = int(float((rh_holdings[stock]['quantity'])))
            bought_price[stock] = float((rh_holdings[stock]['average_buy_price']))
        except:
            holdings[stock] = 0
            bought_price[stock] = 0
    
    return(holdings, bought_price)

def sell(stock, holdings, price, p_sma):
    # go 10 cents less to ensure you sell all of your stocks, not actually 10 cents less
    sell_price = round((price-0.1), 2) 
    sell_order = rh.orders.order_sell_limit(symbol=stock,
                                            quantity=holdings,
                                            limitPrice=sell_price,
                                            timeInForce='gfd')
    print(sell_order)
    if sell_order == {'detail': 'Sell may cause PDT designation.'}:
        print('Sell may cause PDT designation, cannot place the order.')
    
    else:
        print(f'### Trying to SELL {stock} at ${price}')

        current_timezone = pytz.timezone("US/Mountain")
        f = open("log.txt", "a")
        f.write(f"Sell action: {holdings} {stock} at {sell_price} per stock. SMA at time: {p_sma} ---{dt.datetime.now(current_timezone)}---\n")
        f.close()

def buy(stock, allowable_holdings, p_sma):
    # 10 cents up
    buy_price = round((price+0.1), 2) 
    buy_order = rh.orders.order_buy_limit(symbol=stock,
                                            quantity=allowable_holdings,
                                            limitPrice=buy_price,
                                            timeInForce='gfd')

    print(f'### Trying to BUY {stock} at ${price}')
    print(buy_order)
    
    current_timezone = pytz.timezone("US/Mountain")
    f = open("log.txt", "a")
    f.write(f"Buy action: {allowable_holdings} {stock} at {price} per stock. SMA at time: {p_sma} ---{dt.datetime.now(current_timezone)}---\n")
    f.close()

if __name__ == "__main__":
    
    login(days=1)
    
    # Logging section
    current_timezone = pytz.timezone("US/Mountain")
    f = open("log.txt", "a")
    f.write(f"Program started: {dt.datetime.now(current_timezone)}\n")
    f.close()

    stocks = get_stocks()
    print('Stocks: ', stocks)
    cash, equity = get_cash()
    print(f'RH Cash: {cash} RH Equity: {equity}')

    ts = trade_strat.Trader(stocks)
    
    while open_market():
       
        prices = rh.stocks.get_latest_price(stocks)
        holdings, bought_price = get_holdings_and_bought_price(stocks)
        print(f'holdings: {holdings}')
        #print(f'bought price: {bought_price}')
      
        for i, stock in enumerate(stocks):
            price = float(prices[i])
            print(f'\n{stock} = {price}')
                
            df_prices = ts.get_historical_prices(stock, span='week')
            sma = ts.get_sma(stock, df_prices, window=12)
            p_sma = ts.get_price_sma(price, sma)
            print('p_sma:', p_sma)
            trade = ts.trade_option(stock, price)
            print('trade: ', trade)

            if trade == "BUY":
                # Variable to keep us from spending all of our money on a single stock.
                allowable_holdings = int((cash/10)/price)

                print(f"Allowable Holdings: {allowable_holdings}") 
                if allowable_holdings >= 1:
                    if holdings[stock] < allowable_holdings:
                        modified_holdings = allowable_holdings - holdings[stock]
                        buy(stock, modified_holdings, p_sma)
                        print(modified_holdings)
                        #print('### Buy Intention to bring us up to the allowable holdings.') # Dummy placeholder
                    elif holdings[stock] == 0:
                        buy(stock, allowable_holdings, p_sma)
                        #print('### Buy Intention') # Dummy placeholder
                    else:
                      print('### Good to buy, but we have our maximum allowed stock.')                      
                else:
                  print('### Good to buy, no allowable holdings available.')
            elif trade == "SELL":
                if holdings[stock] > 0:
                    sell(stock, holdings[stock], price, p_sma)
                    #print('### Sell Intention') # Dummy placeholder
                else:
                    print('### Good to sell, but we have no stock currently.')
        
        # 2 minute intervals
        time.sleep(120)

    logout()