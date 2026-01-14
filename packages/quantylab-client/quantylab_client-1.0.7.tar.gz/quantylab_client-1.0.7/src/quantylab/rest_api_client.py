import time
import datetime
from pytz import timezone

import pandas as pd
import requests


API_BASE = "https://api.quantylab.com"
DEFAULT_REQ_INTERVAL = 1
FORMAT_DATE = "%Y%m%d"


def get_today():
    dt = datetime.datetime.fromtimestamp(time.time(), timezone("Asia/Seoul"))
    date = dt.date()
    return date


def get_today_str():
    str_today = get_today().strftime(FORMAT_DATE)
    return str_today


def parse_date_str(date_str):
    return datetime.datetime.strptime(date_str, FORMAT_DATE)


def get_past_date(n=20, base_date=None):
    if base_date is None:
        base_date = get_today()
    if type(base_date) is str:
        base_date = parse_date_str(base_date)
    d = base_date - datetime.timedelta(days=n)
    return d


def get_past_date_str(n=20, base_date=None):
    return get_past_date(n=n, base_date=base_date).strftime(FORMAT_DATE)


def req(func):
    def wrapper(self, *args, **kwargs):
        itv = time.time() - self.last_request_time
        if itv < DEFAULT_REQ_INTERVAL:
            time.sleep(DEFAULT_REQ_INTERVAL - itv)
        self.last_request_time = time.time()
        return func(self, *args, **kwargs)
    return wrapper


class QuantylabRestApiClient:
    def __init__(self, token):
        assert token is not None
        self.token = token
        self.last_request_time = 0
        self.headers = {
            "Authorization": f"Bearer {token}",
        }

    def _fetch_all_pages(self, url):
        data = []
        while True:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                raise Exception(f"Request failed: {res.status_code} {res.text}")
            _data = res.json()
            if not _data:
                break
            data.extend(_data["data"])
            if not _data.get("next"):
                break
            url = f"{API_BASE}{_data.get('next')}"
            time.sleep(DEFAULT_REQ_INTERVAL)
        return data

    @req
    def get_stock_market_candles(self, code, start_date=None, end_date=None):
        if end_date is None:
            end_date = get_today_str()
        if start_date is None:
            start_date = get_past_date_str(20, base_date=end_date)
        url = f"{API_BASE}/stock-market-candles?code={code}&start_date={start_date}&end_date={end_date}"
        data = self._fetch_all_pages(url)
        df = pd.DataFrame(data)
        return df

    @req
    def get_stock_fa(self, code, start_date=None, end_date=None):
        if end_date is None:
            end_date = get_today_str()
        if start_date is None:
            start_date = get_past_date_str(20, base_date=end_date)
        url = f"{API_BASE}/stock-fa/?code={code}&start_date={start_date}&end_date={end_date}"
        data = self._fetch_all_pages(url)
        df = pd.DataFrame(data)
        return df

    @req
    def get_investor_buy_sell(self, code, start_date=None, end_date=None):
        if end_date is None:
            end_date = get_today_str()
        if start_date is None:
            start_date = get_past_date_str(20, base_date=end_date)
        url = f"{API_BASE}/investor-buy-sell/?code={code}&start_date={start_date}&end_date={end_date}"
        data = self._fetch_all_pages(url)
        for item in data:
            item.update(item.pop("content"))
        df = pd.DataFrame(data)
        return df

    @req
    def get_investor_top_net_buy_stocks(self, year, investor_type):
        assert investor_type in ["ind", "inst", "foreign"]
        url = f"{API_BASE}/investor-top-net-buy-stocks/?year={year}&investor_type={investor_type}"
        data = self._fetch_all_pages(url)
        df = pd.DataFrame(data)
        return df

    @req
    def get_yearly_investor_avg_profits(self, year):
        url = f"{API_BASE}/yearly-investor-avg-profits/?year={year}"
        data = self._fetch_all_pages(url)
        df = pd.DataFrame(data)
        return df
