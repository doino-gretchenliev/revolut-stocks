import copy
import lxml.etree as etree

from libs import NAP_DATE_FORMAT, NAP_DIGIT_PRECISION
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


def save_to_xml(tree, filename):
    tree.write(filename, pretty_print=True, encoding="utf-8", xml_declaration=True)


def generate_app5_table2(dec50, sales):
    app5 = etree.SubElement(dec50, "app5")
    table2 = etree.SubElement(app5, "table2")
    total_profit = decimal.Decimal(0)
    total_loss = decimal.Decimal(0)
    for sale in sales:
        rowenum = etree.SubElement(table2, "rowenum")
        etree.SubElement(rowenum, "code").text = "508"
        etree.SubElement(rowenum, "transferdate").text = str(sale["trade_date"])
        etree.SubElement(rowenum, "sellvalue").text = str(sale["sell_price"])
        etree.SubElement(rowenum, "buyvalue").text = str(sale["purchase_price"])
        etree.SubElement(rowenum, "profit").text = str(sale["profit"])
        etree.SubElement(rowenum, "loss").text = str(abs(sale["loss"]))
        etree.SubElement(rowenum, "egn").text = ""
        etree.SubElement(rowenum, "name").text = ""

        total_profit += sale["profit"]
        total_loss += abs(sale["loss"])

    etree.SubElement(app5, "t2row6pr").text = str(total_profit)
    etree.SubElement(app5, "t2row6ls").text = str(total_loss)

    diff = (total_profit - total_loss).quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
    if diff > 0:
        etree.SubElement(app5, "t2row7").text = str(diff)
        etree.SubElement(app5, "part2row1").text = str(diff)
        etree.SubElement(app5, "part2row4").text = str(diff)
    else:
        etree.SubElement(app5, "t2row7").text = "0"


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


def generate_app8_part1(app8, purchases):
    aggregated_data = []

    stocks = etree.SubElement(app8, "stocks")
    for stock_symbol, stock_queue in purchases.items():
        if stock_queue:
            comment = etree.Comment(f" === {stock_symbol} === ")
            stocks.append(comment)

        aggregated_stock_data = aggregate_stock_data_by_date(stock_queue)

        for purchase in aggregated_stock_data:
            stocksenum = etree.SubElement(stocks, "stocksenum")
            etree.SubElement(stocksenum, "country").text = "САЩ"
            etree.SubElement(stocksenum, "count").text = str(purchase["quantity"])
            etree.SubElement(stocksenum, "acquiredate").text = str(purchase["trade_date"].strftime(NAP_DATE_FORMAT))
            etree.SubElement(stocksenum, "priceincurrency").text = str(
                (purchase["price_usd"] * purchase["quantity"]).quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
            )
            etree.SubElement(stocksenum, "price").text = str(
                (purchase["price"] * purchase["quantity"]).quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
            )

            purchase["stock_symbol"] = stock_symbol
            aggregated_data.append(purchase)

    return aggregated_data


def generate_app8_part4_1(app8, dividends):
    part38al1 = etree.SubElement(app8, "part38al1")

    owe_tax_total = 0
    for dividend in dividends:
        comment = etree.Comment(f" === {dividend['stock_symbol']} === ")
        part38al1.append(comment)
        rowenum = etree.SubElement(part38al1, "rowenum")
        etree.SubElement(rowenum, "name").text = dividend["company"]
        etree.SubElement(rowenum, "country").text = "САЩ"
        etree.SubElement(rowenum, "incomecode").text = "8141"
        etree.SubElement(rowenum, "methodcode").text = "1"
        etree.SubElement(rowenum, "sum").text = str(
            dividend["gross_profit_amount"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
        )
        etree.SubElement(rowenum, "value").text = "0"
        etree.SubElement(rowenum, "diff").text = "0"
        etree.SubElement(rowenum, "paidtax").text = str(
            dividend["paid_tax_amount"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
        )
        etree.SubElement(rowenum, "permitedtax").text = "0"
        etree.SubElement(rowenum, "tax").text = "0"

        owe_tax_total += dividend["owe_tax"]
        etree.SubElement(rowenum, "owetax").text = str(
            dividend["owe_tax"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
        )

    if owe_tax_total != 0:
        etree.SubElement(app8, "sum81al1").text = str(owe_tax_total.quantize(decimal.Decimal(NAP_DIGIT_PRECISION)))


def export_to_xml(filename, dividends, sales=None, purchases=None):
    aggregated_data = None

    dec50 = etree.Element("dec50")

    app8 = etree.SubElement(dec50, "app8")
    generate_app8_part4_1(app8, dividends)

    if sales is not None:
        generate_app5_table2(dec50, sales)

    if purchases is not None:
        aggregated_data = generate_app8_part1(app8, purchases)

    tree = etree.ElementTree(dec50)
    save_to_xml(tree, filename)

    return aggregated_data