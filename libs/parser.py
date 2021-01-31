import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
from pdfreader.viewer import PageDoesNotExist
from datetime import datetime, timedelta
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs import (
    REVOLUT_DATE_FORMAT,
    REVOLUT_ACTIVITY_TYPES,
    REVOLUT_CASH_ACTIVITY_TYPES,
    REVOLUT_ACTIVITIES_PAGES_INDICATORS,
)


def get_activity_range(page_strings):
    begin_index = 0
    end_index = 0
    for index, page_string in enumerate(page_strings):
        if page_string == "Amount":
            begin_index = index
            continue

        if page_string == "SWEEP ACTIVITY":
            end_index = index
            break

    return begin_index + 1, end_index


def extract_symbol_description(begin_index, page_strings):
    symbol_description = ""
    symbol = ""
    end_index = begin_index
    for page_string in page_strings[begin_index:]:
        try:
            decimal.Decimal(clean_number(page_string))
            break
        except decimal.InvalidOperation:
            symbol_description += page_string
        end_index += 1

    symbol = symbol_description[0 : symbol_description.index("-") - 1]
    return end_index, symbol, symbol_description


def clean_number(number_string):
    return number_string.replace("(", "").replace(")", "").replace(",", "")


def extract_activity(begin_index, page_strings, num_fields):
    end_index, symbol, symbol_description = extract_symbol_description(begin_index + 4, page_strings)

    activity = {
        "trade_date": datetime.strptime(page_strings[begin_index], REVOLUT_DATE_FORMAT),
        "settle_date": datetime.strptime(page_strings[begin_index + 1], REVOLUT_DATE_FORMAT),
        "currency": page_strings[begin_index + 2],
        "activity_type": page_strings[begin_index + 3],
        "symbol_description": symbol_description,
    }

    if num_fields == 8:
        activity["symbol"] = symbol
        activity["quantity"] = decimal.Decimal(page_strings[end_index])
        activity["price"] = decimal.Decimal(page_strings[end_index + 1])
        activity["amount"] = page_strings[end_index + 2]
    elif num_fields == 6:
        activity["amount"] = page_strings[end_index]

    activity["amount"] = decimal.Decimal(clean_number(activity["amount"]))

    return activity


def extract_activities(viewer):
    activities = []

    while True:
        viewer.render()
        page_strings = viewer.canvas.strings

        if page_strings and page_strings[0] in REVOLUT_ACTIVITIES_PAGES_INDICATORS:
            begin_index, end_index = get_activity_range(page_strings)
            page_strings = page_strings[begin_index:end_index]
            for index, page_string in enumerate(page_strings):
                if page_string in REVOLUT_ACTIVITY_TYPES:
                    activity = extract_activity(index - 3, page_strings, 8)
                elif page_string in REVOLUT_CASH_ACTIVITY_TYPES:
                    activity = extract_activity(index - 3, page_strings, 6)
                else:
                    continue

                activities.append(activity)

        try:
            viewer.next()
        except PageDoesNotExist:
            break

    return activities


def find_place_position(statements, date):
    pos = 0
    for statement in statements:
        if statement["trade_date"] > date:
            break

        pos += 1

    return pos


def parse_statements(statement_files):
    statements = []

    for statement_file in statement_files:
        with open(statement_file, "rb") as fd:
            viewer = SimplePDFViewer(fd)
            activities = extract_activities(viewer)
            if not activities:
                continue
            statements.append(activities)

    statements = sorted(statements, key=lambda k: k[0]["trade_date"])
    return [activity for activities in statements for activity in activities]
