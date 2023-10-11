import requests
import json
import time
import config

#Define time period for RSI indicator and set authentification token
today_now = int(time.time())
two_weeks_ago = today_now - (2*604800)
token="finnhub-token"
    
#Set base URLs
ORDERS_URL = '{}/v2/orders'.format(config.APCA_API_BASE_URL)
DATA_URL = '{}/api/v1'.format(config.FH_API_DATA_URL)
    
stocks = ['AMD', 'WMT', 'AAPL', 'TSLA', 'GME', 'AMZN']
    
for x in stocks: 
    ticker = x
        
    #Set position URL
    POSITIONS_URL = '{}/v2/positions/{}'.format(config.APCA_API_BASE_URL, ticker)

    #See if ticker position is open by getting position data, if no position data, exception thrown
    try:
        position = requests.get(url=POSITIONS_URL, headers=config.HEADERS)
        p_json = position.json()
        entry = float(p_json['cost_basis'])
        exit = float(p_json['market_value'])
        plpc = ((exit - entry) / ((entry + exit) / 2)) * 100
        has_position = True
    except:
        has_position = False

    #Get RSI technical indicator data from Finnhub API 
    RSI_URL = '{}/indicator?symbol={}&resolution=D&from={}&to={}&indicator=rsi&timeperiod=3&token={}'.format(
    DATA_URL, ticker, two_weeks_ago, today_now, token)
    rsi_data = requests.get(url=RSI_URL)
    rsi_json = rsi_data.json()

    #Get ticker data from Finnhub API
    ticker_info = requests.get(url='{}/quote?symbol={}&token={}'.format(DATA_URL, ticker, token))
    ticker_json = ticker_info.json()
    ticker_positive = ticker_json['c'] > ticker_json['o']

    if list(rsi_json['rsi'])[-1] < 38 and ticker_positive and not has_position :
        #Set market order data
        data = {
            'symbol': ticker,
            'qty': 5,
            'side': 'buy',
            'type': 'market',
            'time_in_force': 'gtc'
        }
        requests.post(url=ORDERS_URL, json=data, headers=config.HEADERS)
        print("Bought")
    elif has_position and (plpc > 5 or plpc < -2.5):
        #Set market order data
        data = {
            'symbol': ticker,
                'qty': 5,
            'side': 'sell',
            'type': 'market',
            'time_in_force': 'gtc'
        }
        requests.post(url=ORDERS_URL, json=data, headers=config.HEADERS)
        print("Sold")
    else:
        print("Conditions not met")