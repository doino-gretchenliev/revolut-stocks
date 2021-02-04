from libs.exchange_rates import populate_exchange_rates
from libs.calculators.default import calculate_win_loss, calculate_dividends
from libs.csv import export_statements, export_app8_part1, export_app5_table2, export_app8_part4_1
from libs.xml import export_to_xml
import libs.parsers

import sys
import os
import logging
import importlib
from pkgutil import iter_modules

logger = logging.getLogger("process")

supported_parsers = {}
if getattr(sys, "frozen", False):
    import libs.parsers.revolut as revolut
    import libs.parsers.trading212 as trading212
    import libs.parsers.csv as csv

    supported_parsers = {"revolut": revolut.Parser, "trading212": trading212.Parser, "csv": csv.Parser}
else:
    parser_modules = [mod.name for mod in iter_modules(libs.parsers.__path__, "libs.parsers.")]
    for parser_module in parser_modules:
        if not parser_module.endswith("parser"):
            parser = importlib.import_module(parser_module).Parser
            parser_name = parser_module.split(".")[-1]
            supported_parsers[parser_name] = parser


def process(input_dir, output_dir, parser_name, use_bnb):
    logger.debug(f"Supported parsers: [{supported_parsers}]")

    logger.info(f"Parsing statement files.")
    parser = None
    try:
        parser = supported_parsers[parser_name](input_dir)
        statements = parser.parse()
    except KeyError:
        logger.error(f"Unsupported parser: [{parser_name}].")
        raise SystemExit(1)

    logger.info(f"Generating [statements.csv] file.")
    export_statements(os.path.join(output_dir, "statements.csv"), statements)

    if not statements:
        logger.error(f"Not activities found. Please, check your statement files.")
        raise SystemExit(1)

    logger.info(f"Populating exchange rates.")
    populate_exchange_rates(statements, use_bnb)

    logger.info(f"Calculating dividends information.")
    dividends = calculate_dividends(statements)

    logger.info(f"Generating [app8-part4-1.csv] file.")
    export_app8_part4_1(os.path.join(output_dir, "app8-part4-1.csv"), dividends)

    sales = None
    purchases = None
    unsupported_activity_types = parser.get_unsupported_activity_types(statements)

    if len(unsupported_activity_types) == 0:
        logger.info(f"Calculating sales information.")
        sales, purchases = calculate_win_loss(statements)

        logger.info(f"Generating [app5-table2.csv] file.")
        export_app5_table2(os.path.join(output_dir, "app5-table2.csv"), sales)

    logger.info(f"Generating [dec50_2020_data.xml] file.")
    export_to_xml(os.path.join(output_dir, "dec50_2020_data.xml"), dividends, sales, purchases)

    if purchases is not None:
        logger.info(f"Generating [app8-part1.csv] file.")
        export_app8_part1(os.path.join(output_dir, "app8-part1.csv"), purchases)

    if sales is not None:
        win_loss = sum(item["profit"] + item["loss"] for item in sales)
        logger.info(f"Profit/Loss: {win_loss} lev.")

    if unsupported_activity_types:
        logger.warning(
            f"Statements contain unsupported activity types: {unsupported_activity_types}. Only dividends related data was calculated."
        )
