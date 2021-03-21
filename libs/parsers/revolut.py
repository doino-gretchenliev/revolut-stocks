import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
from pdfreader.viewer import PageDoesNotExist
from datetime import datetime, timedelta
import re
import logging
import decimal


decimal.getcontext().rounding = decimal.ROUND_HALF_UP

from libs import RECEIVED_DIVIDEND_ACTIVITY_TYPES, TAX_DIVIDEND_ACTIVITY_TYPES
from libs.utils import list_statement_files
from libs.parsers.parser import StatementFilesParser

logger = logging.getLogger("parsers")

REVOLUT_DATE_FORMAT = "%m/%d/%Y"

REVOLUT_ACTIVITY_TYPES = ["SELL", "SELL CANCEL", "BUY", "SSP", "SSO", "MAS"] + RECEIVED_DIVIDEND_ACTIVITY_TYPES + TAX_DIVIDEND_ACTIVITY_TYPES
REVOLUT_CASH_ACTIVITY_TYPES = ["CDEP", "CSD"]
REVOLUT_OUT_OF_ORDER_ACTIVITY_TYPES = ["SSP", "MAS"]
REVOLUT_UNSUPPORTED_ACTIVITY_TYPES = ["SC", "NC", "MA"]
REVOLUT_NO_COMPANY_ACTIVITY_TYPES = ["SSO"]
REVOLUT_ACTIVITIES_PAGES_INDICATORS = ["Balance Summary", "ACTIVITY", "Equity"]
REVOLUT_DIGIT_PRECISION = "0.00000001"


class ActivitiesNotFound(Exception):
    pass


class Parser(StatementFilesParser):
    def get_activity_range(self, page_strings):
        begin_index = None
        end_index = None

        for index, page_string in enumerate(page_strings):
            if page_string == "ACTIVITY":
                begin_index = index
                continue

            if page_string == "SWEEP ACTIVITY":
                end_index = index
                break

        if begin_index is None:
            raise ActivitiesNotFound()

        if end_index is None:
            end_index = len(page_strings)

        logger.debug(f"Found begin index: [{begin_index}] and end index: [{end_index}]")
        return begin_index + 1, end_index

    def extract_symbol(self, symbol_description):
        try:
            return symbol_description[0 : symbol_description.index("-") - 1]
        except ValueError:
            logger.error(f"Unable to extract stock symbol from description:[{symbol_description}].")
            raise SystemExit(1)

    def extract_symbol_description(self, begin_index, page_strings):
        symbol_description = ""
        end_index = begin_index
        for page_string in page_strings[begin_index:]:
            try:
                decimal.Decimal(self.clean_number(page_string))
                break
            except decimal.InvalidOperation:
                symbol_description += page_string
            end_index += 1

        if page_strings[end_index - 1] in REVOLUT_CASH_ACTIVITY_TYPES:
            symbol_description = None

        return end_index, symbol_description

    def clean_number(self, number_string):
        return number_string.replace("(", "").replace(")", "").replace(",", "")

    def get_stock_company(self, symbol_description):
        company = None
        second_sep_index = None
        try:
            first_sep_index = symbol_description.index("-") + 1
            company = symbol_description[first_sep_index:]
            second_sep_index = len(company)
            if "-" in company:
                second_sep_index = company.index("-")
        except ValueError:
            logger.error("Unable to extract stock company.")
            raise SystemExit(1)

        return re.sub(r"\s{2,}", " ", company[:second_sep_index].strip())

    def extract_activity(self, begin_index, page_strings, num_fields):
        logger.debug(f"Page string: {page_strings}")
        end_index, symbol_description = self.extract_symbol_description(begin_index + 4, page_strings)
        symbol = None
        if symbol_description is not None:
            symbol = self.extract_symbol(symbol_description)

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
            if activity["activity_type"] not in REVOLUT_NO_COMPANY_ACTIVITY_TYPES:
                activity["company"] = self.get_stock_company(symbol_description)
        elif num_fields == 6:
            activity["amount"] = page_strings[end_index]

        activity["amount"] = decimal.Decimal(self.clean_number(activity["amount"]))

        return activity

    def extract_activities(self, viewer):
        activities = []

        while True:
            viewer.render()
            page_strings = viewer.canvas.strings

            logger.debug(f"Parsing page [{viewer.current_page_number}]")

            if page_strings:
                logger.debug(f"First string on the page: [{page_strings[0]}]")

                if page_strings[0] in REVOLUT_ACTIVITIES_PAGES_INDICATORS:
                    try:
                        begin_index, end_index = self.get_activity_range(page_strings)
                        page_strings = page_strings[begin_index:end_index]
                        for index, page_string in enumerate(page_strings):
                            if page_string in REVOLUT_ACTIVITY_TYPES:
                                activity = self.extract_activity(index - 3, page_strings, 8)
                            elif page_string in REVOLUT_CASH_ACTIVITY_TYPES:
                                activity = self.extract_activity(index - 3, page_strings, 6)
                            else:
                                continue

                            activities.append(activity)
                    except ActivitiesNotFound:
                        pass

            try:
                viewer.next()
            except PageDoesNotExist:
                break

        return activities

    def get_first_non_ssp_activity_index(self, statements):
        for index, statement in enumerate(statements):
            if statement["activity_type"] not in REVOLUT_OUT_OF_ORDER_ACTIVITY_TYPES:
                return index

    def parse(self):
        statements = []

        statement_files = list_statement_files(self.input_dir, "pdf")
        if not statement_files:
            logger.error(f"No statement files found.")
            raise SystemExit(1)

        logger.info(f"Collected statement files for processing: {statement_files}.")

        for statement_file in statement_files:
            logger.debug(f"Processing statement file[{statement_file}]")

            with open(statement_file, "rb") as fd:
                viewer = SimplePDFViewer(fd)
                activities = self.extract_activities(viewer)
                if not activities:
                    continue
                statements.append(activities)

        statements = sorted(statements, key=lambda k: k[self.get_first_non_ssp_activity_index(k)]["trade_date"])
        return [activity for activities in statements for activity in activities]

    @staticmethod
    def get_unsupported_activity_types(statements):
        unsupported_activity_types = []
        for statement in statements:
            if statement["activity_type"] in REVOLUT_UNSUPPORTED_ACTIVITY_TYPES:
                unsupported_activity_types.append(statement["activity_type"])

        return list(set(unsupported_activity_types))