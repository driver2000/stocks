from datetime import date, timedelta

import requests
from retry import retry

from .resources import API_TOKEN, BASE_URL, CODES
from .utils import to_unix_timestamp


@retry(requests.exceptions.HTTPError, delay=2, jitter=(1, 3), backoff=2, max_delay=3)
def _retrive(url):
    res = requests.get(url, headers={"X-Finnhub-Token": API_TOKEN})
    res.raise_for_status()
    data = res.json()
    return data


def get_stock_statics():
    for code in CODES:
        res = _retrive(BASE_URL + f"stock/profile2?symbol={code}")
        if res:
            yield code, res


def get_stock_histories(codes):
    start = to_unix_timestamp(date.today() - timedelta(days=365))
    end = to_unix_timestamp(date.today())
    for code in codes:
        res = _retrive(BASE_URL + f"stock/candle?symbol={code}&resolution=D&from={start}&to={end}")
        if res and res["s"] == "ok":
            yield [code, zip(res["c"], res["t"])]


def get_fx_rates():
    return [
        x
        for x in _retrive(BASE_URL + "forex/symbol?exchange=oanda")
        if x["displaySymbol"] in ("EUR/USD", "AUD/USD", "GBP/USD")
    ]


def get_fx_histories(codes):
    start = to_unix_timestamp(date.today() - timedelta(days=365))
    end = to_unix_timestamp(date.today())
    for code in codes:
        res = _retrive(BASE_URL + f"forex/candle?symbol={code}&resolution=D&from={start}&to={end}")
        if res and res["s"] == "ok":
            yield [code, zip(res["c"], res["t"])]


def get_fx_rate_from_usd(code):
    return _retrive(BASE_URL + "/forex/rates?base=USD")["quote"].get(code)
