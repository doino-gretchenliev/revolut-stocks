# Author Borislav Gizdov <borislav.gizdov@gmail.com>
from libs.parsers.parser import StatementFilesParser
from libs.utils import list_statement_files
from libs import RECEIVED_DIVIDEND_ACTIVITY_TYPES, TAX_DIVIDEND_ACTIVITY_TYPES
import csv
from datetime import datetime, timedelta
import logging
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


logger = logging.getLogger("parsers")

RECEIVED_DIVIDEND_ACTIVITY_TYPES = [
    "DIV", "DIVIDEND", "DIVCGL", "DIVCGS", "DIVROC", "DIVTXEX"]
TAX_DIVIDEND_ACTIVITY_TYPES = ["DIVNRA", "DIVFT", "DIVTW"]

PASSFOLIO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
PASSFOLIO_ACTIVITY_TYPES = [
    "SELL", "BUY"] + RECEIVED_DIVIDEND_ACTIVITY_TYPES + TAX_DIVIDEND_ACTIVITY_TYPES
PASSFOLIO_CASH_ACTIVITY_TYPES = []
PASSFOLIO_OUT_OF_ORDER_ACTIVITY_TYPES = []
PASSFOLIO_UNSUPPORTED_ACTIVITY_TYPES = []
PASSFOLIO_ACTIVITIES_PAGES_INDICATORS = []
PASSFOLIO_DIGIT_PRECISION = "0.00000001"

ORDERS_REQUIRED_COLUMNS = ["orderId", "enteredAt", "executedAt", "status", "side",
                           "type", "symbol", "filledQuantity", "quantity", "amount", "price", "service", "feesUSD"]
DIVIDENDS_REQUIRED_COLUMNS = ["receivedAt", "reinvested", "reinvestedAt", "reinvestedAmount", "isAdjustment",
                              "amount", "amountPerShare", "symbol", "type", "taxCode", "description", "taxAmount", "taxRate"]


class ActivitiesNotFound(Exception):
    pass

class Parser(StatementFilesParser):
    def read_headers(self, header_row, required_columns):
        headers = {column_name.replace(
            " ", "_"): index for index, column_name in enumerate(header_row)}

        missing_required_columns = []
        for required_column in required_columns:
            if required_column not in headers:
                missing_required_columns.append(required_column)

        if missing_required_columns:
            logger.error(
                f"Found missing required columns: {missing_required_columns}.")
            raise SystemExit(1)

        return headers

    def clean_number(self, number_string):
        return number_string.replace("(", "").replace(")", "").replace(",", "")

    def extract_activities(self, viewer, file_name):
        activities = []

        headers = None

        for index, row in enumerate(viewer):
            if "orders" in file_name:
                if index == 0 and "orders" in file_name:
                    headers = self.read_headers(row, ORDERS_REQUIRED_COLUMNS)
                if index < 1:
                    continue

                if not row:
                    continue

                if row[headers["enteredAt"]] == '' or row[headers["executedAt"]] == '':
                    continue

                if row[headers["side"]] in PASSFOLIO_ACTIVITY_TYPES:
                    activity = {
                        "trade_date": datetime.strptime(row[headers["enteredAt"]], PASSFOLIO_DATE_FORMAT).replace(tzinfo=None),
                        "settle_date": datetime.strptime(row[headers["executedAt"]], PASSFOLIO_DATE_FORMAT).replace(tzinfo=None),
                        "currency": 'USD',
                        "activity_type": row[headers["side"]],
                        "symbol_description": row[headers["symbol"]],
                        "symbol": row[headers["symbol"]],
                        "quantity": decimal.Decimal(self.clean_number(row[headers["quantity"]])),
                        "price": decimal.Decimal(self.clean_number(row[headers["price"]])),
                        "amount": decimal.Decimal(self.clean_number(row[headers["amount"]])),
                        "company": row[6],
                    }

                    activities.append(activity)

            if "dividends" in file_name:
                if index == 0 and "dividends" in file_name:
                    headers = self.read_headers(
                        row, DIVIDENDS_REQUIRED_COLUMNS)

                if index < 1:
                    continue

                if not row:
                    continue

                activity = {
                    "trade_date": datetime.strptime(row[headers["receivedAt"]], PASSFOLIO_DATE_FORMAT).replace(tzinfo=None),
                    "settle_date": datetime.strptime(row[headers["receivedAt"]], PASSFOLIO_DATE_FORMAT).replace(tzinfo=None),
                    "currency": 'USD',
                    "activity_type": 'DIV',
                    "symbol_description": row[headers["description"]],
                    "symbol": row[headers["symbol"]],
                    "quantity":  decimal.Decimal(self.clean_number(row[headers["amount"]])) * decimal.Decimal(self.clean_number(row[headers["amountPerShare"]])),
                    "price": decimal.Decimal(self.clean_number(row[headers["amountPerShare"]])),
                    "amount": decimal.Decimal(self.clean_number(row[headers["amount"]])),
                    "company": row[6],
                }

                activities.append(activity)

        return activities

    def parse(self):
        statements = []

        statement_files = list_statement_files(self.input_dir, "csv")
        if not statement_files:
            logger.error(f"No statement files found.")
            raise SystemExit(1)

        logger.info(
            f"Collected statement files for processing: {statement_files}.")

        for statement_file in statement_files:
            logger.debug(f"Processing statement file[{statement_file}]")

            with open(statement_file, "r") as fd:
                viewer = csv.reader(fd, delimiter=",")
                activities = self.extract_activities(viewer, statement_file)
                if not activities:
                    continue
                statements.append(activities)

        statements = sorted(statements, key=lambda k: k[0]["trade_date"])
        return [activity for activities in statements for activity in activities]

    @staticmethod
    def get_unsupported_activity_types(statements):
        unsupported_activity_types = []
        for statement in statements:
            if statement["activity_type"] in PASSFOLIO_UNSUPPORTED_ACTIVITY_TYPES:
                unsupported_activity_types.append(statement["activity_type"])

        return list(set(unsupported_activity_types))
