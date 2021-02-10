from libs import (
    NAP_DIGIT_PRECISION,
    NAP_DIVIDEND_TAX,
    BNB_DATE_FORMAT,
    NAP_DATE_FORMAT,
    RECEIVED_DIVIDEND_ACTIVITY_TYPES,
    TAX_DIVIDEND_ACTIVITY_TYPES,
)
from libs.calculators.utils import get_avg_purchase_price, adjust_quantity, adjust_stock_data, aggregate_purchases

from collections import deque
import logging

logger = logging.getLogger("calculations")

import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


def calculate_win_loss(statements):
    purchases = {}
    sales = []
    ssp_surrendered_data = {}
    for statement in statements:
        stock_symbol = statement.get("symbol", None)

        if statement["activity_type"] == "BUY":
            activity_quantity = abs(statement.get("quantity", 0))

            logger.debug(
                f"[BUY] [{stock_symbol}] td:[{statement['trade_date']}] qt:[{activity_quantity}] pr:[{statement['price']}] ex:[{statement['exchange_rate']}]"
            )
            stock_queue = purchases.get(stock_symbol, deque())
            stock_queue.append(
                {
                    "price": statement["price"],
                    "exchange_rate": statement["exchange_rate"],
                    "quantity": activity_quantity,
                    "trade_date": statement["trade_date"],
                }
            )
            purchases[stock_symbol] = stock_queue

        if statement["activity_type"] == "SELL":
            activity_quantity = abs(statement.get("quantity", 0))

            logger.debug(
                f"[SELL] [{stock_symbol}] td:[{statement['trade_date']}] qt:[{activity_quantity}] pr:[{statement['price']}] ex:[{statement['exchange_rate']}]"
            )

            if stock_symbol not in purchases or len(purchases[stock_symbol]) == 0:
                logging.warn(f"No purchase information found for: [{stock_symbol}].")
                continue

            stock_queue = purchases[stock_symbol]

            logger.debug(f"Before adjustment: {stock_queue}")

            avg_purchase_price, avg_purchase_price_in_currency = get_avg_purchase_price(stock_queue)
            logger.debug(f"AVG price: [{avg_purchase_price}]")

            purchase_price = avg_purchase_price * activity_quantity
            sell_price = statement["amount"] * statement["exchange_rate"]

            purchase_price_in_currency = avg_purchase_price_in_currency * activity_quantity
            sell_price_in_currency = statement["amount"]

            sale = {
                "symbol": stock_symbol,
                "trade_date": statement["trade_date"].strftime(NAP_DATE_FORMAT),
                "avg_purchase_price": avg_purchase_price,
                "purchase_price": purchase_price.quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "sell_price": sell_price.quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "sell_exchange_rate": statement["exchange_rate"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "profit": decimal.Decimal(0),
                "loss": decimal.Decimal(0),
                "profit_in_currency": decimal.Decimal(0),
                "loss_in_currency": decimal.Decimal(0),
            }

            profit_loss = (sale["sell_price"] - sale["purchase_price"]).quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
            if profit_loss > 0:
                sale["profit"] = profit_loss
            else:
                sale["loss"] = profit_loss

            profit_loss = (sell_price_in_currency - purchase_price_in_currency).quantize(
                decimal.Decimal(NAP_DIGIT_PRECISION)
            )
            if profit_loss > 0:
                sale["profit_in_currency"] = profit_loss
            else:
                sale["loss_in_currency"] = profit_loss

            sales.append(sale)

            adjust_quantity(stock_queue, activity_quantity)
            logger.debug(f"After adjustment: {purchases[stock_symbol]}")

        if statement["activity_type"] == "SSO":
            activity_quantity = abs(statement.get("quantity", 0))

            logger.debug(
                f"[SSO] [{stock_symbol}] td:[{statement['trade_date']}] qt:[{activity_quantity}] pr:[{statement['price']}] ex:[{statement['exchange_rate']}]"
            )

            stock_queue = purchases.get(stock_symbol, deque())
            stock_queue.append(
                {
                    "price": decimal.Decimal(0),
                    "exchange_rate": decimal.Decimal(0),
                    "quantity": activity_quantity,
                    "trade_date": statement["trade_date"],
                }
            )
            purchases[stock_symbol] = stock_queue

        if statement["activity_type"] == "SSP" or statement["activity_type"] == "MAS":
            activity_type = statement["activity_type"]
            activity_quantity = statement["quantity"]
            stock_symbol = stock_symbol.replace(".OLD", "")

            logger.debug(
                f"[{activity_type}] [{stock_symbol}] td:[{statement['trade_date']}] qt:[{activity_quantity}] pr:[{statement['price']}] ex:[{statement['exchange_rate']}]"
            )

            if activity_quantity < 0:
                ssp_surrendered_data[stock_symbol] = {
                    "quantity": abs(activity_quantity),
                    "price": statement["price"],
                }
                continue

            stock_queue = purchases.get(stock_symbol, deque())
            logger.debug(f"Before addition: {stock_queue}")

            if stock_symbol not in ssp_surrendered_data:
                logging.warn(f"No SSP surrender information found for: [{stock_symbol}].")
                continue

            surrendered_data = ssp_surrendered_data[stock_symbol]
            ssp_quantity_ratio = abs(activity_quantity) / surrendered_data["quantity"]
            ssp_price_ratio = statement["price"] / surrendered_data["price"]

            logger.debug(f"SSP quantity ratio: [{ssp_quantity_ratio}], price ratio: [{ssp_price_ratio}].")
            adjust_stock_data(stock_queue, ssp_quantity_ratio, ssp_price_ratio)
            logger.debug(f"After addition: {stock_queue}")
            del ssp_surrendered_data[stock_symbol]

    return sales, calculate_remaining_purchases(purchases)


def calculate_remaining_purchases(purchases):
    result = {}
    for stock_symbol, stock_queue in aggregate_purchases(purchases).items():

        calculated_queue = []
        for purchase in stock_queue:
            calculated_queue.append(
                {
                    **purchase,
                    **{
                        "price_in_currency": (purchase["price"] * purchase["quantity"]).quantize(
                            decimal.Decimal(NAP_DIGIT_PRECISION)
                        ),
                        "price": (purchase["price"] * purchase["exchange_rate"] * purchase["quantity"]).quantize(
                            decimal.Decimal(NAP_DIGIT_PRECISION)
                        ),
                    },
                }
            )
        result[stock_symbol] = calculated_queue

    return result


def calculate_dividends_tax(dividends):
    result = []
    for stock_symbol, stock_queue in dividends.items():
        for dividend in stock_queue:
            owe_tax = decimal.Decimal(0)
            if dividend["paid_tax_amount"] == 0:
                owe_tax = dividend["gross_profit_amount"] * decimal.Decimal(NAP_DIVIDEND_TAX)

            found_same_company_dividend = False
            for stock_data in result:
                if stock_data["stock_symbol"] == stock_symbol:
                    stock_data["paid_tax_amount"] += dividend["paid_tax_amount"]
                    stock_data["gross_profit_amount"] += dividend["gross_profit_amount"]
                    stock_data["owe_tax"] += owe_tax
                    found_same_company_dividend = True
                    break

            if not found_same_company_dividend:
                result.append({**dividend, **{"stock_symbol": stock_symbol, "owe_tax": owe_tax}})
    return result


def calculate_dividends(statements):
    dividends = {}
    for statement in statements:

        if (
            statement["activity_type"] in RECEIVED_DIVIDEND_ACTIVITY_TYPES
            or statement["activity_type"] in TAX_DIVIDEND_ACTIVITY_TYPES
        ):
            stock_symbol = statement["symbol"]
            activity_amount = statement["amount"] * statement["exchange_rate"]

            logger.debug(f"[{statement['activity_type']}] [{stock_symbol}] am:[{activity_amount}]")

            if statement["activity_type"] in RECEIVED_DIVIDEND_ACTIVITY_TYPES:
                stock_queue = dividends.get(stock_symbol, deque())
                stock_queue.append(
                    {
                        "company": statement["company"],
                        "gross_profit_amount": activity_amount,
                        "paid_tax_amount": decimal.Decimal(0),
                    }
                )
                dividends[stock_symbol] = stock_queue
                continue

            if statement["activity_type"] in TAX_DIVIDEND_ACTIVITY_TYPES:
                if stock_symbol not in dividends:
                    logging.error(f"No previous dividend information found for: [{stock_symbol}].")
                    raise SystemExit(1)

                stock_queue = dividends[stock_symbol]
                stock_queue[-1]["paid_tax_amount"] = (
                    stock_queue[-1].get("paid_tax_amount", decimal.Decimal(0)) + activity_amount
                )

    return calculate_dividends_tax(dividends)
