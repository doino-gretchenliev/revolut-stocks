import argparse
import os
import logging

from libs.exchange_rates import populate_exchange_rates
from libs.calculations import calculate_win_loss, calculate_dividends
from libs.parser import parse_statements
from libs.utils import list_statement_files
from libs.csv import export_statements, export_app8_part1, export_app5_table2, export_app8_part4_1
from libs.xml import export_to_xml

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")
logger = logging.getLogger("main")

parser = argparse.ArgumentParser(description="Revolut stock calculator for NAP.")
parser.add_argument(
    "-i", dest="input_dir", help="Directory containing Revolut statement files(in pdf format).", required=True
)
parser.add_argument(
    "-o",
    dest="output_dir",
    help="Output directory for csv files. Directory will be populated with NAP calculations and verification documents in csv format.",
    required=True,
)
parser.add_argument("-b", dest="use_bnb", help="Use BNB online service as exchange rates source.", action="store_true")
parser.add_argument("-v", dest="verbose", help="Enable verbose output.", action="store_true")
parsed_args = parser.parse_args()

if parsed_args.verbose:
    logging.getLogger("calculations").setLevel(level=logging.DEBUG)
    logging.getLogger("exchange_rates").setLevel(level=logging.DEBUG)


def main():
    logger.info("Collecting statement files.")
    statement_files = list_statement_files(parsed_args.input_dir)

    if not statement_files:
        logger.error(f"No statement files found.")
        raise SystemExit(1)

    logger.info(f"Collected statement files for processing: {statement_files}.")

    logger.info(f"Parsing statement files.")
    statements = parse_statements(statement_files)

    logger.info(f"Generating [statements.csv] file.")
    export_statements(os.path.join(parsed_args.output_dir, "statements.csv"), statements)

    logger.info(f"Populating exchange rates.")
    populate_exchange_rates(statements, parsed_args.use_bnb)

    logger.info(f"Generating [app8-part1.csv] file.")
    export_app8_part1(os.path.join(parsed_args.output_dir, "app8-part1.csv"), statements)

    logger.info(f"Calculating sales information.")
    sales = calculate_win_loss(statements)

    logger.info(f"Generating [app5-table2.csv] file.")
    export_app5_table2(os.path.join(parsed_args.output_dir, "app5-table2.csv"), sales)

    logger.info(f"Calculating dividends information.")
    dividends = calculate_dividends(statements)

    logger.info(f"Generating [app8-part4-1.csv] file.")
    export_app8_part4_1(os.path.join(parsed_args.output_dir, "app8-part4-1.csv"), dividends)

    logger.info(f"Generating [dec50_2020_data.xml] file.")
    export_to_xml(os.path.join(parsed_args.output_dir, "dec50_2020_data.xml"), statements, sales, dividends)

    win_loss = sum(item["profit"] + item["loss"] for item in sales)
    logger.info(f"Profit/Loss: {win_loss} lev.")


if __name__ == "__main__":
    main()