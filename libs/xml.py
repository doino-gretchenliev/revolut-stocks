import lxml.etree as etree

from libs import NAP_DATE_FORMAT, NAP_DIGIT_PRECISION
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


def save_to_xml(tree, filename):
    tree.write(filename, pretty_print=True, encoding="utf-8", xml_declaration=True)


def generate_app5_table2(dec50, sales):
    app5 = etree.SubElement(dec50, "app5")
    table2 = etree.SubElement(app5, "table2")
    total_profit = 0
    total_loss = 0
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
    else:
        etree.SubElement(app5, "t2row7").text = "0"


def generate_app8_part1(app8, statements):
    stocks = etree.SubElement(app8, "stocks")
    for statement in statements:
        if statement["activity_type"] == "BUY":
            stocksenum = etree.SubElement(stocks, "stocksenum")
            etree.SubElement(stocksenum, "country").text = "САЩ"
            etree.SubElement(stocksenum, "count").text = str(statement["quantity"])
            etree.SubElement(stocksenum, "acquiredate").text = str(statement["trade_date"].strftime(NAP_DATE_FORMAT))
            etree.SubElement(stocksenum, "priceincurrency").text = str(statement["price"])
            etree.SubElement(stocksenum, "price").text = str(
                (statement["price"] * statement["exchange_rate"]).quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
            )


def generate_app8_part4_1(app8, dividends):
    part38al1 = etree.SubElement(app8, "part38al1")
    for dividend in dividends:
        rowenum = etree.SubElement(part38al1, "rowenum")
        etree.SubElement(rowenum, "name").text = "DriveWealth LLC"
        etree.SubElement(rowenum, "country").text = "САЩ"
        etree.SubElement(rowenum, "incomecode").text = "8141"
        etree.SubElement(rowenum, "methodcode").text = "1"
        etree.SubElement(rowenum, "sum").text = str(dividend["gross_profit_amount"])
        etree.SubElement(rowenum, "value").text = "0"
        etree.SubElement(rowenum, "diff").text = "0"
        etree.SubElement(rowenum, "paidtax").text = str(dividend["paid_tax_amount"])
        etree.SubElement(rowenum, "permitedtax").text = "0"
        etree.SubElement(rowenum, "tax").text = "0"
        etree.SubElement(rowenum, "owetax").text = "0"


def export_to_xml(filename, statements, sales, dividends):
    dec50 = etree.Element("dec50")

    generate_app5_table2(dec50, sales)

    app8 = etree.SubElement(dec50, "app8")
    generate_app8_part1(app8, statements)
    generate_app8_part4_1(app8, dividends)

    tree = etree.ElementTree(dec50)
    save_to_xml(tree, filename)