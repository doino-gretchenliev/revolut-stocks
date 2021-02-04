import csv
from datetime import datetime, timedelta
import logging
import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs.utils import list_statement_files
from libs.parsers.parser import StatementFilesParser

logger = logging.getLogger("parsers")

CSV_DATE_FORMATS = [
    "%d.%m.%Y",
    "%Y.%m.%d",
    "%m-%d-%Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%Y/%m/%d",
]
CSV_ACTIVITY_TYPES = ["SELL", "BUY", "DIV", "DIVNRA", "SSP", "MAS"]
CSV_REQUIRED_COLUMNS = ["trade_date", "activity_type", "company", "symbol", "quantity", "price", "amount"]


class Parser(StatementFilesParser):
    def parse_date(self, date_string):
        for date_format in CSV_DATE_FORMATS:
            try:
                return datetime.strptime(date_string, date_format)
            except ValueError:
                pass

        logger.error(f"Unable to parse date: [{date_string}].")
        raise SystemExit(1)

    def clean_number(self, number_string):
        return number_string.replace("(", "").replace(")", "").replace(",", "")

    def read_headers(self, header_row):
        headers = {column_name.replace(" ", "_").lower(): index for index, column_name in enumerate(header_row)}
        print(headers)

        missing_required_columns = []
        for required_column in CSV_REQUIRED_COLUMNS:
            if required_column not in headers:
                missing_required_columns.append(required_column)

        if missing_required_columns:
            logger.error(f"Found missing required columns: {missing_required_columns}.")
            raise SystemExit(1)

        return headers

    def extract_activities(self, viewer):
        activities = []

        headers = None
        for index, row in enumerate(viewer):
            if index == 0:
                headers = self.read_headers(row)

            if not row:
                continue

            if row[headers["activity_type"]] in CSV_ACTIVITY_TYPES:
                activity = {
                    "trade_date": self.parse_date(row[headers["trade_date"]]),
                    "settle_date": "-",
                    "currency": "USD",
                    "activity_type": row[headers["activity_type"]],
                    "symbol": row[headers["symbol"]],
                    "company": row[headers["company"]],
                    "symbol_description": row[headers["symbol"]] + " - " + row[headers["company"]],
                    "quantity": decimal.Decimal(self.clean_number(row[headers["quantity"]])),
                    "price": decimal.Decimal(self.clean_number(row[headers["price"]])),
                    "amount": decimal.Decimal(self.clean_number(row[headers["amount"]])),
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
                statements.extend(activities)

        return statements

    def get_unsupported_activity_types(self, statements):
        return []