import config
import trade_strat
import os
import robin_stocks.robinhood as rh
import datetime as dt
import time
import pytz
import pyotp

# This will login as of 09-30-2021
# Program WILL execute buy and sell orders now, must be aware of this. Can buy and sell, have dummy print statements for testing new things.
# Crypto buy-sell with same strategy?

# CURRENT SETTING: SMA calculated over 1 week of historicals data, longer term strat than Day-Trading to avoid any restrictions. 
# TEST WEEK: week of 10/04/2021 - 10/08/2021
# Monday Value: $375.69 (Saturday)
# Tuesday Value:
# Wednesday Value:
# Thursday Value:
# Friday Value:

totp = pyotp.TOTP(os.environ["AUTH_APP"]).now()
#print('Current OTP: ', totp)

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
    stocks = list()
    stocks.append('NOK')
    stocks.append('PLTR')
    stocks.append('SOFI')
    stocks.append('F')
    stocks.append('KR')
    stocks.append('GPRO')
    stocks.append('EM')
    stocks.append('GE')
    stocks.append('CEI')
    stocks.append('PFE')
    stocks.append('ACB')
    stocks.append('DAL')
    stocks.append('BB')
    stocks.append('SBUX')
    stocks.append('T')
    stocks.append('TWTR')
    stocks.append('UBER')
    stocks.append('GM')
    stocks.append('CRON')
    stocks.append('SIRI')
    stocks.append('RBLX')
    stocks.append('MRO')
    stocks.append('RIOT')
    stocks.append('ET')
    stocks.append('SONY') # 24 Stocks monitoring as of 10/2/2021
    
    return(stocks)

# Market hours function
def open_market():
    market = False
    time_now = dt.datetime.now().time()
    

    market_open = dt.time(13,30,0) # 7:30 am
    market_close = dt.time(19,59,0) # 1:59 pm

    if time_now > market_open and time_now < market_close:
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

def sell(stock, holdings, price):
    # go 10 cents less to ensure you sell all of your stocks, not actually 10 cents less
    sell_price = round((price-0.1), 2) 
    sell_order = rh.orders.order_sell_limit(symbol=stock,
                                            quantity=holdings,
                                            limitPrice=sell_price,
                                            timeInForce='gfd')
    
    print(f'### Trying to SELL {stock} at ${price}')

    current_timezone = pytz.timezone("US/Mountain")
    f = open("log.txt", "a")
    f.write(f"Sell action: {holdings} {stock} at {sell_price} per stock. ---{dt.datetime.now(current_timezone)}---\n")
    f.close()

def buy(stock, allowable_holdings):
    # 10 cents up
    buy_price = round((price+0.1), 2) 
    buy_order = rh.orders.order_buy_limit(symbol=stock,
                                            quantity=allowable_holdings,
                                            limitPrice=buy_price,
                                            timeInForce='gfd')

    print(f'### Trying to BUY {stock} at ${price}')
    
    current_timezone = pytz.timezone("US/Mountain")
    f = open("log.txt", "a")
    f.write(f"Buy action: {allowable_holdings} {stock} at {price} per stock. ---{dt.datetime.now(current_timezone)}---\n")
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
            print('\n{} = ${}'.format(stock, price))
            
            df_prices = ts.get_historical_prices(stock, span='week')
            sma = ts.get_sma(stock, df_prices, window=12)
            p_sma = ts.get_price_sma(price, sma)
            print('p_sma:', p_sma)
            trade = ts.trade_option(stock, price)
            print('trade: ', trade)
            if trade == "BUY":
                allowable_holdings = int((cash/10)/price)
                print(f"Allowable Holdings: {allowable_holdings}") 
                if allowable_holdings > 2 and holdings[stock] == 0:
                    #buy(stock, allowable_holdings)
                    print('### Buy Intention') # Dummy placeholder
                else:
                   print('### Good to buy, no allowable holdings available.')
            elif trade == "SELL":
                if holdings[stock] > 0:
                    #sell(stock, holdings[stock], price)
                    print('### Sell Intention') # Dummy placeholder
                else:
                    print('### Good to sell, but we have not stock.')
        
        time.sleep(30)

    logout()