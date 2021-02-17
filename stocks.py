import argparse
import logging

from libs.process import process, supported_parsers

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")

parser = argparse.ArgumentParser(description="Revolut stock calculator for NAP.")
parser.add_argument("-i", dest="input_dir", help="Directory containing Revolut statement files(in pdf format).", required=False)
parser.add_argument(
    "-o",
    dest="output_dir",
    help="Output directory for csv files. Directory will be populated with NAP calculations and verification documents in csv format.",
    required=True,
)
parser.add_argument(
    "-p",
    dest="parsers",
    action="append",
    help=("Parsers to use for statement processing. You can use argument multiple times to use more than one parser. Default: revolut."),
    choices=supported_parsers,
    required=False,
)
parser.add_argument("-b", dest="use_bnb", help="Use BNB online service as exchange rates source.", action="store_true")
parser.add_argument("-c", dest="in_currency", help="Show profit/loss in currency.", action="store_true")
parser.add_argument("-v", dest="verbose", help="Enable verbose output.", action="store_true")
parsed_args = parser.parse_args()

if parsed_args.verbose:
    logging.getLogger("calculations").setLevel(level=logging.DEBUG)
    logging.getLogger("exchange_rates").setLevel(level=logging.DEBUG)
    logging.getLogger("parsers").setLevel(level=logging.DEBUG)
    logging.getLogger("process").setLevel(level=logging.DEBUG)


def main():
    parsers = parsed_args.parsers
    if parsers is None:
        parsers = ["revolut"]

    process(
        parsed_args.input_dir,
        parsed_args.output_dir,
        parsers,
        parsed_args.use_bnb,
        parsed_args.in_currency,
    )


if __name__ == "__main__":
    main()
