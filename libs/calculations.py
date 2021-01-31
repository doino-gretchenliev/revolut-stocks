from libs import REVOLUT_DIGIT_PRECISION, NAP_DIGIT_PRECISION, BNB_DATE_FORMAT, NAP_DATE_FORMAT

from collections import deque
import logging

logger = logging.getLogger("calculations")

import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


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


def calculate_win_loss(statements):
    purchases = {}
    sales = []
    for statement in statements:
        stock_symbol = statement.get("symbol", None)
        activity_quantity = abs(statement.get("quantity", 0))

        if statement["activity_type"] == "BUY":
            logger.debug(
                f"[New purchase] [{stock_symbol}] td:[{statement['trade_date']}] qt:[{activity_quantity}] pr:[{statement['price']}] ex:[{statement['exchange_rate']}]"
            )
            stock_queue = purchases.get(stock_symbol, deque())
            stock_queue.append(
                {"price": statement["price"] * statement["exchange_rate"], "quantity": activity_quantity}
            )
            purchases[stock_symbol] = stock_queue

        if statement["activity_type"] == "SELL":
            logger.debug(
                f"[New sale] [{stock_symbol}] td:[{statement['trade_date']}] qt:[{activity_quantity}] pr:[{statement['price']}] ex:[{statement['exchange_rate']}]"
            )

            if stock_symbol not in purchases or len(purchases[stock_symbol]) == 0:
                logging.warn(f"No purchase information found for: [{stock_symbol}].")
                continue

            stock_queue = purchases[stock_symbol]

            logger.debug(f"Before adjustment: {stock_queue}")

            avg_purchase_price = get_avg_purchase_price(stock_queue)
            logger.debug(f"AVG price: [{avg_purchase_price}]")

            purchase_price = avg_purchase_price * activity_quantity
            sell_price = statement["amount"] * statement["exchange_rate"]

            sale = {
                "symbol": stock_symbol,
                "trade_date": statement["trade_date"].strftime(NAP_DATE_FORMAT),
                "avg_purchase_price": avg_purchase_price,
                "purchase_price": purchase_price.quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "sell_price": sell_price.quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "sell_exchange_rate": statement["exchange_rate"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "profit": decimal.Decimal(0),
                "loss": decimal.Decimal(0),
            }

            profit_loss = (sale["sell_price"] - sale["purchase_price"]).quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
            if profit_loss > 0:
                sale["profit"] = profit_loss
            else:
                sale["loss"] = profit_loss

            sales.append(sale)

            adjust_quantity(stock_queue, activity_quantity)
            logger.debug(f"After adjustment: {purchases[stock_symbol]}")

    return sales


def calculate_dividends(statements):
    dividends_operations = {}
    dividends = []
    for statement in statements:
        if statement["activity_type"] == "DIV" or statement["activity_type"] == "DIVNRA":
            stock_symbol = statement["symbol"]
            activity_amount = statement["amount"] * statement["exchange_rate"]

            if statement["activity_type"] == "DIV":
                if stock_symbol in dividends_operations:
                    dividends.append(
                        {
                            "symbol": stock_symbol,
                            "gross_profit_amount": (dividends_operations[stock_symbol] + activity_amount).quantize(
                                decimal.Decimal(NAP_DIGIT_PRECISION)
                            ),
                            "paid_tax_amount": 0,
                        }
                    )

                dividends_operations[stock_symbol] = activity_amount

            if statement["activity_type"] == "DIVNRA":
                dividends.append(
                    {
                        "symbol": stock_symbol,
                        "gross_profit_amount": (dividends_operations[stock_symbol] + activity_amount).quantize(
                            decimal.Decimal(NAP_DIGIT_PRECISION)
                        ),
                        "paid_tax_amount": activity_amount.quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                    }
                )
                del dividends_operations[stock_symbol]

    return dividends
