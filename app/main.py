from typing import Optional
from fastapi import FastAPI, HTTPException
import pymongo

app = FastAPI()

connect_str = 'mongodb://admin:admin@18.141.209.89'
client = pymongo.MongoClient(connect_str)
db = client["warehouse_mongo"]

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/dbs/{market}/{symbol}")
def read_data(market: str, symbol: str):
    market = market.lower()
    symbol = symbol.lower()
    if market!='us':
        symbol = symbol + f'.{market}'
    collection_name = f'{market}_financials'
    collection = db[collection_name]
    result = list(collection.find({'symbol': symbol, 'frequency': 'annual'}))
    print(result)
    if len(result) == 0:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    data = { item['statement']:sorted(item['data']['financials'], key = lambda i: i['year'])[-5:] for item in result}
    revenues = [{'year': str(int(item['year'])), 'value': item['revenue']} for item in data['ic']]
    eps = [{'year': str(int(item['year'])), 'value': item['dilutedEPS']} for item in data['ic']]
    cash = [{'year': str(int(item['year'])), 'value': item['cash']} for item in data['bs']]
    de = [{'year': str(int(item['year'])), 'value': item['totalDebt']/item['totalEquity']} for item in data['bs']]
    share = [{'year': str(int(item['year'])), 'value': item['totalCommonSharesOutstanding']} for item in data['bs']]
    out = {'status': 'SUCCESS',
      'result': {
        "recommend": None,
        "target_price" : None, 
        "up_side_down_side_percent": None,
        "items": [{
            "title": "Fundamental",
            "type": "FUNDAMENTAL",
            "items": [{
                "name": "Revenue",
                "period": "YOY",
                "type": "LINE",
                "actual_entries": revenues,
                "forecast_entries": None
            },
            {
                "name": "EPS",
                "period": "YOY",
                "type": "LINE",
                "actual_entries": eps,
                "forecast_entries": None
            },
            {
                "name": "Cash",
                "period": "YOY",
                "type": "LINE",
                "actual_entries": cash,
                "forecast_entries": None
            },
            {
                "name": "D/E",
                "period": "YOY",
                "type": "LINE",
                "actual_entries": de,
                "forecast_entries": None
            },
            {
                "name": "Dividend",
                "period": "YOY",
                "type": "LINE",
                "actual_entries": None,
                "forecast_entries": None
            },
            {
                "name": "Shares",
                "period": "YOY",
                "type": "LINE",
                "actual_entries": share,
                "forecast_entries": None
            }]
        }]
      }}
    return out