import robin_stocks as rh
import datetime as dt
import time

def login(days):
    time_logged_in = 60*60*24*days
    rh.authentication.login(username=,
                            password=,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)