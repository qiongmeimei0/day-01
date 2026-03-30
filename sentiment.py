import requests
from config import *

def fear_greed():
    url = "https://api.alternative.me/fng/"
    r = requests.get(url).json()
    value = int(r['data'][0]['value'])
    if value<30:
      return 1
    elif value>70:
      return -1
    return 0

def news_sentiment():
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {"auth_token": CRYPTOPANIC_KEY, "currencies":"BTC"}
    r = requests.get(url, params=params).json()
    pos, neg = 0,0
    for post in r['results']:
        votes = post['votes']
        pos += votes.get('positive',0)
        neg += votes.get('negative',0)
    if pos>neg:
        return 1
    elif neg>pos:
        return -1
    return 0