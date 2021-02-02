from libs.utils import humanize_date
from libs import NAP_DATE_FORMAT, NAP_DIGIT_PRECISION

import os
import csv
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


def export_to_csv(list_object, csv_file, fieldnames):

    csv_list_object = humanize_date(list_object)

    with open(csv_file, "w") as fd:
        writer = csv.DictWriter(
            fd,
            fieldnames=fieldnames,
            quotechar='"',
            quoting=csv.QUOTE_ALL,
        )

        header = {fieldname: fieldname.replace("_", " ").title() for fieldname in fieldnames}
        writer.writerow(header)
        for elements in csv_list_object:
            writer.writerow(elements)


def export_statements(file_path, statements):
    export_to_csv(
        statements,
        file_path,
        [
            "trade_date",
            "settle_date",
            "currency",
            "activity_type",
            "company",
            "symbol_description",
            "symbol",
            "quantity",
            "price",
            "amount",
        ],
    )


def export_app8_part1(file_path, purchases):
    export_purchases = []
    for stock_symbol, stock_queue in purchases.items():
        for purchase in stock_queue:
            count = purchase["quantity"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION))
            if count > 0:
                export_purchases.append(
                    {
                        **{
                            "stock_symbol": stock_symbol,
                            "count": str(count),
                            "acquire_date": purchase["trade_date"].strftime(NAP_DATE_FORMAT),
                            "purchase_price_in_currency": purchase["price_in_currency"],
                            "purchase_price_in_lev": purchase["price"],
                        },
                    }
                )

    export_to_csv(
        export_purchases,
        file_path,
        ["stock_symbol", "count", "acquire_date", "purchase_price_in_currency", "purchase_price_in_lev"],
    )


def export_app5_table2(file_path, sales):
    sales = [
        {
            **{
                k: v
                for k, v in sale.items()
                if k not in ["symbol", "avg_purchase_price", "sell_exchange_rate", "profit_in_currency", "loss_in_currency"]
            },
            **{"code": 508},
        }
        for sale in sales
    ]
    export_to_csv(
        sales,
        file_path,
        ["code", "trade_date", "sell_price", "purchase_price", "profit", "loss"],
    )


def export_app8_part4_1(file_path, dividend_taxes):
    dividends = [
        {
            **{k: v for k, v in dividend_tax.items() if k not in ["symbol"]},
            **{"profit_code": 8141, "tax_code": 1},
            **{
                "gross_profit_amount": dividend_tax["gross_profit_amount"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "paid_tax_amount": dividend_tax["paid_tax_amount"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
                "owe_tax": dividend_tax["owe_tax"].quantize(decimal.Decimal(NAP_DIGIT_PRECISION)),
            },
        }
        for dividend_tax in dividend_taxes
    ]

    export_to_csv(
        dividends,
        file_path,
        ["stock_symbol", "company", "profit_code", "tax_code", "gross_profit_amount", "paid_tax_amount", "owe_tax"],
    )
