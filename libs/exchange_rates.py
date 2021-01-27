from io import StringIO
import csv
from dateutil.relativedelta import relativedelta
import urllib.request
from urllib.parse import urlencode
from datetime import datetime, timedelta
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs import BNB_BASE_URL, BNB_DATE_FORMAT, BNB_SPLIT_BY_MONTHS, BNB_CSV_HEADER_ROWS


def query_exchange_rates(first_date, last_date):
    params = {
        "downloadOper": "true",
        "group1": "second",
        "valutes": "USD",
        "search": "true",
        "showChart": "false",
        "showChartButton": "false",
        "type": "CSV",
    }

    params["periodStartDays"] = "{:02d}".format(first_date.day)
    params["periodStartMonths"] = "{:02d}".format(first_date.month)
    params["periodStartYear"] = first_date.year

    params["periodEndDays"] = "{:02d}".format(last_date.day)
    params["periodEndMonths"] = "{:02d}".format(last_date.month)
    params["periodEndYear"] = last_date.year

    response = urllib.request.urlopen(BNB_BASE_URL + urlencode(params))
    data = response.read()
    text = data.decode("utf-8")

    f = StringIO(text)
    reader = csv.reader(f, delimiter=",")
    exchange_rates = {}

    for index, row in enumerate(reader):
        if index < BNB_CSV_HEADER_ROWS:
            continue

        if not row:
            continue

        date = datetime.strptime(row[0], BNB_DATE_FORMAT)
        exchange_rates[date] = decimal.Decimal(row[3].strip())

    return exchange_rates


def get_exchange_rates(first_date, last_date):
    first_date -= relativedelta(months=1)  # Get one extra month of data to ensure there was a published exchange rate
    exchange_rates = {}
    while True:
        curr_fs_date = first_date
        curr_ls_date = first_date + relativedelta(months=BNB_SPLIT_BY_MONTHS)
        exchange_rates.update(query_exchange_rates(curr_fs_date, curr_ls_date))
        first_date = curr_ls_date + relativedelta(days=1)

        if first_date > last_date:
            break

    return exchange_rates


def find_last_published_exchange_rate(exchange_rates, search_date):
    return min(exchange_rates.keys(), key=lambda date: abs(date - search_date))


def populate_exchange_rates(statements):
    first_date = statements[0]["trade_date"]
    last_date = statements[-1]["trade_date"]
    exchange_rates = get_exchange_rates(first_date, last_date)
    for statement in statements:
        if statement["trade_date"] in exchange_rates:
            statement["exchange_rate"] = exchange_rates[statement["trade_date"]]
            statement["exchange_rate_date"] = statement["trade_date"]
            continue

        statement["exchange_rate_date"] = find_last_published_exchange_rate(exchange_rates, statement["trade_date"])
        statement["exchange_rate"] = exchange_rates[statement["exchange_rate_date"]]
