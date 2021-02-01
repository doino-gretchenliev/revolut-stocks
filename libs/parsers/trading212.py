import csv
from datetime import datetime, timedelta
import logging
import decimal


decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs.utils import list_statement_files
from libs.parsers.parser import StatementFilesParser

logger = logging.getLogger("parsers")

TRADING212_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
TRADING212_ACTIVITY_TYPES = dict([("Market sell","SELL"), ("Market buy","BUY"), ("Limit sell","SELL"), ("Limit buy","BUY")])
TRADING212_CASH_ACTIVITY_TYPES = []
TRADING212_OUT_OF_ORDER_ACTIVITY_TYPES = []
TRADING212_UNSUPPORTED_ACTIVITY_TYPES = []
TRADING212_ACTIVITIES_PAGES_INDICATORS = []
TRADING212_DIGIT_PRECISION = "0.00000001"


class ActivitiesNotFound(Exception):
    pass


class Parser(StatementFilesParser):

    def clean_number(self, number_string):
        return number_string.replace("(", "").replace(")", "").replace(",", "")

    def extract_activities(self, viewer):
        activities = []

        for index, row in enumerate(viewer):
            if index < 1:
                continue

            if not row:
                continue

            if row[0] in TRADING212_ACTIVITY_TYPES:
                activity = {
                    "trade_date": datetime.strptime(row[1], TRADING212_DATE_FORMAT),
                    "settle_date": '-',
                    "currency": row[7],
                    "activity_type": TRADING212_ACTIVITY_TYPES[row[0]],
                    "symbol_description": row[4] + " " + row[2],
                    "symbol": row[3],
                    "quantity": decimal.Decimal(row[5]),
                    "price": decimal.Decimal(row[6]),
                    "amount": decimal.Decimal(self.clean_number(row[10])),
                    "company": row[4]
                }

                activities.append(activity)

        return activities

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

        statements = sorted(statements, key=lambda k: k[0]["trade_date"])
        return [activity for activities in statements for activity in activities]

    def get_unsupported_activity_types(self, statements):
        unsupported_activity_types = []
        for statement in statements:
            if statement["activity_type"] in TRADING212_UNSUPPORTED_ACTIVITY_TYPES:
                unsupported_activity_types.append(statement["activity_type"])

        return list(set(unsupported_activity_types))