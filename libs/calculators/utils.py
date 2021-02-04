import copy
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs import NAP_DATE_FORMAT, NAP_DIGIT_PRECISION


def get_avg_purchase_price(stock_queue):
    if len(stock_queue) == 1:
        return stock_queue[0]["price"]

    price = 0
    quantity = 0
    for data in stock_queue:
        price += data["price"] * data["quantity"]
        quantity += data["quantity"]

    return price / quantity


def adjust_quantity(stock_queue, sold_quantity):
    quantity_to_adjust = sold_quantity

    for data in list(stock_queue):
        quantity_after_abj = data["quantity"] - quantity_to_adjust

        if quantity_after_abj > 0:
            data["quantity"] = quantity_after_abj
            break

        stock_queue.popleft()
        quantity_to_adjust -= data["quantity"]


def aggregate_stock_data_by_date(stock_queue):
    queue = copy.deepcopy(stock_queue)
    aggregated_stock_data = []

    for purchase in queue:

        found_same_date_purchase = False
        for data in aggregated_stock_data:
            if purchase["trade_date"] == data["trade_date"] and purchase["price_usd"] == data["price_usd"]:
                data["quantity"] += purchase["quantity"]
                found_same_date_purchase = True

        if not found_same_date_purchase:
            aggregated_stock_data.append(purchase)

    return aggregated_stock_data


def aggregate_purchases(purchases):
    result = {}
    for stock_symbol, stock_queue in purchases.items():
        if len(stock_queue) > 0:
            result[stock_symbol] = aggregate_stock_data_by_date(stock_queue)
    return result
