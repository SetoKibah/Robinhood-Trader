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
# CURRENT SETTING: SMA with month setting and with Daytrading allowable_holdings.

# 01/11/2022: Defense Threshold of -8% has been set, as well as a profit sale of 8% for testing purposes. Will adjust and update. Returning bot to 24/7 runtime mode.
###############################################################

totp = pyotp.TOTP(os.environ["AUTH_APP"]).now()
print('Current OTP: ', totp)
#time.sleep(180)

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

    #current_timezone = pytz.timezone("US/Mountain")
    #f = open("log.txt", "a")
    #f.write(f"Logout: {dt.datetime.now(current_timezone)}\n")
    #f.close()

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
              'PFE',
              'ACB',
              'DAL',
              'BB',
              'SBUX',
              'T',
              'IMCC',
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
              'DKNG',
              'BAC',
              'PYPL',
              'WFC',
              'TFC',
              'UBS',
              'VEOEY',
              'ROL',
              'XOM',
              'EQNR',
              'D',
              'VMW',
              'MCFE',
              'ABNB',
              'VG',
              'UAL',
              'BIDU',
              'DIS',
              'BTCM',
              'SNDL',
              'NIO',
              'OXY',
              'EC']
    print(f"###{len(stocks)} STOCKS CURRENTLY MONITORED###")
    random.shuffle(stocks)
    return(stocks)

def set_ticker_conditions():
    tickers = get_stocks()
    for stock in stocks:
      db[stock] = True
      


# Market hours function
def open_market():
    # Market is set to closed unless conditions are met
    market = False
    time_now = dt.datetime.now().time()

    # Weekday 0-6, 0 is Monday, 6 is Sunday
    weekday = dt.datetime.now().weekday()

    market_open = dt.time(14,33,0) # 7:32 am
    market_close = dt.time(20,58,0) # 1:58 pm

    if time_now > market_open and time_now < market_close and weekday < 5:
        market = True
        
    else:
      print('### Market is closed.')


    return(market)

# Function to cash on account
def get_cash():
    rh_cash = rh.account.build_user_profile()

    rh_profile = rh.account.load_account_profile()
    buying_power = float(rh_profile['buying_power'])
    
    # Use this if we want ot hold money in reserve
    #cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])

    # Replace with cash if we want to hold money in reserve
    return(buying_power, equity)

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
        print('Sell may cause PDT designation, cannot place the order today.')
    
    else:
        print(f'### Trying to SELL {stock} at ${price}')

        current_timezone = pytz.timezone("US/Mountain")
        f = open("log.txt", "a")
        f.write(f"Sell action: {holdings} {stock} at ${sell_price:.2f} per stock. SMA at time: {p_sma:2} ---{dt.datetime.now(current_timezone):%m-%d-%Y, %H:%M:%S}---\n")
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
    f.write(f"Buy action: {allowable_holdings} {stock} at ${price:.2f} per stock. SMA at time: {p_sma:2} ---{dt.datetime.now(current_timezone):%m-%d-%Y, %H:%M:%S}---\n")
    f.close()

if __name__ == "__main__":
    
    login(days=1)
    
    # Logging section
    current_timezone = pytz.timezone("US/Mountain")
    #f = open("log.txt", "a")
    #f.write(f"Program started: {dt.datetime.now(current_timezone)}\n")
    #f.close()
    #####################################################
    #rh_cash_test = rh.account.build_user_profile()
    #print(rh_cash_test)

    #rh_cash_test = rh.account.load_account_profile()
    #print(rh_cash_test.keys())
    #####################################################
    #print('Test End...')
    #time.sleep(30)
    
    
    stocks = get_stocks()
    #print('Stocks: ', stocks)
    cash, equity = get_cash()
    print(f'RH Cash: {cash} RH Equity: {equity}')

    ts = trade_strat.Trader(stocks)

    #print(f"{stocks[0]}: {db[stocks[0]]}")
    
    
    while open_market():
       
        prices = rh.stocks.get_latest_price(stocks)
        holdings, bought_price = get_holdings_and_bought_price(stocks)
        print(f'holdings: {holdings}')
        print(f'bought price: {bought_price}')
        
        # Traverse the stock listings and make decisions on each ticker.
        for i, stock in enumerate(stocks):

            # Check if stock is set to False
            if db[stock] == False:
              break
            # If stock condition is True, carry out the task.
            else:
                # Get price value
                price = float(prices[i])
                print(f'\n{stock} = ${price}')
                print(f'Average bought price: ${round(bought_price[stock], 4)}')

                # Sell_Threshold should be set to 8 percent above the bought price
                sell_threshold = round(bought_price[stock] * 1.08, 2)
                # Defense sale price to mitigate losses in an event
                defense_threshold = round(bought_price[stock] * 0.92, 2)
                # Historical prices
                df_prices = ts.get_historical_prices(stock, span='month')
                # Simple Moving Average calculation
                sma = ts.get_sma(stock, df_prices, window=12)
                # Price over SMA calculation
                p_sma = ts.get_price_sma(price, sma)
                print('p_sma:', p_sma)
                trade = ts.trade_option(stock, price)
                print('trade: ', trade)

                # Check against the defensive threshold, sell the stock if the condition is met and set DB to False.
                if price < defense_threshold:
                  print(f"{stock} has gone below {defense_threshold}. Freezing stock.")
                  sell(stock, holdings[stock], price, p_sma)
                  db[stock] = False
                  break
                
                else:

                    if trade == "BUY":
                        # Variable to keep us from spending all of our money on a single stock.
                        allowable_holdings = int((cash/10)/price)
                        # Small check to make sure our values don't trigger false positives
                        if allowable_holdings < 0:
                            allowable_holdings = allowable_holdings * -1

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
                            # Check to see if selling now will give a profit. If not, do not sell
                            if price < sell_threshold:
                                print(f"Refusing to sell. Current price: ${price} --- Average Purchase Price: ${bought_price[stock]} --- Defense Threshold: ${defense_threshold}.")
                            else:
                                sell(stock, holdings[stock], price, p_sma)
                                #print('### Sell Intention') # Dummy placeholder
                        else:
                              print('### Good to sell, but we have no stock currently.')
        
        # 10 minute intervals
        time.sleep(600)
          
    logout()

    