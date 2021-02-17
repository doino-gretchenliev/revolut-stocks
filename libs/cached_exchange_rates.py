from datetime import datetime
import decimal
import json

decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs import BNB_DATE_FORMAT

def load_exchange_rates():
    result = {}

    with open("local_exchange_rates.json") as f:
        exchange_rates = json.load(f)

    for date, exchange_rate in exchange_rates.items():
        date = datetime.strptime(date, BNB_DATE_FORMAT)
        result[date] = decimal.Decimal(exchange_rate)

    return result