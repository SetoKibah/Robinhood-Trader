# Automatic Trading Algorithm

Custom Trading Algorithm using Robinhood platform.

This is an automatic trading script, using the Price over SMA calculation to determine appropriate trade behaviors, and utilizes the *robin_stocks* api.

Packages used:

- robin_stocks
- datetime
- time
- pytz
- pyotp
- replit db

Using the above packages, we keep a database of current Stock Tickers (hardcoded in) with a binary value of True/False. True means a stock is monitored and traded freely. False means a stock is considered "frozen", has been sold, and will not be traded until it has stabilized. 