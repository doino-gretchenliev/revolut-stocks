import csv
from datetime import datetime, timedelta
import re
import logging
import decimal


decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs import RECEIVED_DIVIDEND_ACTIVITY_TYPES, TAX_DIVIDEND_ACTIVITY_TYPES
from libs.utils import list_statement_files
from libs.parsers.parser import StatementFilesParser

logger = logging.getLogger("parsers")

REVOLUT_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

REVOLUT_ACTIVITY_TYPES = ["SELL", "SELL CANCEL", "BUY", "SSP", "SSO", "MAS", "SC"] + RECEIVED_DIVIDEND_ACTIVITY_TYPES + TAX_DIVIDEND_ACTIVITY_TYPES
REVOLUT_CASH_ACTIVITY_TYPES = ["CDEP", "CSD", "CASH TOP-UP", "CASH WITHDRAWAL"]
REVOLUT_OUT_OF_ORDER_ACTIVITY_TYPES = ["SSP", "MAS"]
REVOLUT_UNSUPPORTED_ACTIVITY_TYPES = ["NC", "MA"]
REVOLUT_NO_COMPANY_ACTIVITY_TYPES = ["SSO"]
REVOLUT_DIGIT_PRECISION = "0.00000001"


class ActivitiesNotFound(Exception):
    pass


class Parser(StatementFilesParser):
    def extract_activities(self, viewer):
        activities = []

        for index, row in enumerate(viewer):
            if index < 1:
                continue

            if not row:
                continue

            if row[2] in REVOLUT_ACTIVITY_TYPES:
                activity = {
                    "trade_date": datetime.strptime(row[0], REVOLUT_DATE_FORMAT),
                    "settle_date": datetime.strptime(row[0], REVOLUT_DATE_FORMAT),
                    "currency": row[6],
                    "activity_type": row[2],
                    "symbol_description": row[1],
                    "symbol": row[1],
                    "quantity": decimal.Decimal(row[3]) if row[3] else None,
                    "price": decimal.Decimal(row[4]) if row[4] else None,
                    "amount": decimal.Decimal(row[5]),
                    "company": row[1],
                }

                activities.append(activity)

        return activities

    def get_first_non_out_of_order_activity_index(self, statements):
        for index, statement in enumerate(statements):
            if statement["activity_type"] not in REVOLUT_OUT_OF_ORDER_ACTIVITY_TYPES:
                return index

        return None

    def get_sorting_date(self, statements):
        sorting_index = self.get_first_non_out_of_order_activity_index(statements)

        if sorting_index is None:
            if not self.sorting_dates:
                logger.error("No previous purchase information found for out of order activities.")
                raise SystemExit(1)

            return self.sorting_dates[-1]

        trade_date = statements[sorting_index]["trade_date"]
        self.sorting_dates.append(trade_date)
        return trade_date

    def parse(self):
        statements = []

        statement_files = list_statement_files(self.input_dir, "csv")
        if not statement_files:
            logger.error(f"No statement files found.")
            raise SystemExit(1)

        logger.info(f"Collected statement files for processing: {statement_files}.")

        for statement_file in statement_files:
            logger.debug(f"Processing statement file[{statement_file}]")

            with open(statement_file, "r") as fd:
                viewer = csv.reader(fd, delimiter=",")
                activities = self.extract_activities(viewer)
                if not activities:
                    continue
                statements.append(activities)

        self.sorting_dates = []
        statements = sorted(statements, key=lambda k: self.get_sorting_date(k))

        from pprint import pprint

        print(pprint(statements))
        return [activity for activities in statements for activity in activities]

    @staticmethod
    def get_unsupported_activity_types(statements):
        unsupported_activity_types = []
        for statement in statements:
            if statement["activity_type"] in REVOLUT_UNSUPPORTED_ACTIVITY_TYPES:
                unsupported_activity_types.append(statement["activity_type"])

        return list(set(unsupported_activity_types))
