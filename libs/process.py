from libs.exchange_rates import populate_exchange_rates
from libs.calculators.fifo import calculate_sales, calculate_remaining_purchases, calculate_dividends, calculate_dividends_tax, calculate_win_loss
from libs.csv import export_statements, export_app8_part1, export_app5_table2, export_app8_part4_1
from libs.xml import export_to_xml
from libs.utils import merge_dict_of_dicts, merge_dict_of_lists, get_unsupported_activity_types
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


def for_each_parser(func, statements, filename=None, output_dir=None, **kwargs):
    result = {}
    for parser_name, parser_statements in statements.items():
        if filename is not None:
            if len(statements) > 1:
                parser_output_dir = os.path.join(output_dir, parser_name)
                kwargs["file_path"] = os.path.join(parser_output_dir, filename)
                os.makedirs(parser_output_dir, exist_ok=True)
            else:
                kwargs["file_path"] = os.path.join(output_dir, filename)
                os.makedirs(output_dir, exist_ok=True)

        result[parser_name] = func(**{"statements": parser_statements}, **kwargs)

    return result


def process(input_dir, output_dir, parser_names, use_bnb, in_currency=False):
    logger.debug(f"Supported parsers: [{supported_parsers}]")

    parser_names = list(dict.fromkeys(parser_names))

    logger.info(f"Parsing statement files with parsers: {parser_names}.")
    statements = {}
    for parser_name in parser_names:
        parser_input_dir = input_dir
        if len(parser_names) > 1:
            parser_input_dir = os.path.join(parser_input_dir, parser_name)

        statements[parser_name] = supported_parsers[parser_name](parser_input_dir).parse()

        if not statements[parser_name]:
            logger.error(f"Not activities found with parser[{parser_name}]. Please, check the statement files.")
            raise SystemExit(1)

    logger.info(f"Generating statements file.")
    for_each_parser(
        export_statements,
        statements,
        filename="statements.csv",
        output_dir=output_dir,
    )

    logger.info(f"Populating exchange rates.")
    for_each_parser(populate_exchange_rates, statements, use_bnb=use_bnb)

    logger.info(f"Calculating dividends information.")
    dividends = for_each_parser(calculate_dividends, statements)
    merged_dividends = merge_dict_of_dicts(dividends)
    dividend_taxes = calculate_dividends_tax(merged_dividends)

    logger.info(f"Generating [app8-part4-1.csv] file.")
    export_app8_part4_1(os.path.join(output_dir, "app8-part4-1.csv"), dividend_taxes)

    parsers_calculations = None
    merged_sales = None
    remaining_purchases = None

    unsupported_activity_types = get_unsupported_activity_types(supported_parsers, statements)

    if len(unsupported_activity_types) == 0:
        logger.info(f"Calculating sales information.")
        parsers_calculations = for_each_parser(calculate_sales, statements)

        logger.info(f"Generating [app5-table2.csv] file.")
        sales = {parser_name: parser_calculations[0] for parser_name, parser_calculations in parsers_calculations.items()}
        purchases = {parser_name: parser_calculations[1] for parser_name, parser_calculations in parsers_calculations.items()}

        merged_sales = merge_dict_of_lists(sales)
        merged_purchases = merge_dict_of_dicts(purchases)
        remaining_purchases = calculate_remaining_purchases(merged_purchases)

        export_app5_table2(os.path.join(output_dir, "app5-table2.csv"), merged_sales)

    logger.info(f"Generating [dec50_2020_data.xml] file.")
    export_to_xml(
        os.path.join(output_dir, "dec50_2020_data.xml"),
        dividend_taxes,
        merged_sales if merged_sales is not None else None,
        remaining_purchases if remaining_purchases is not None else None,
    )

    if remaining_purchases is not None:
        logger.info(f"Generating [app8-part1.csv] file.")
        export_app8_part1(os.path.join(output_dir, "app8-part1.csv"), remaining_purchases)

    if merged_sales is not None:
        win_loss, win_loss_in_currency = calculate_win_loss(merged_sales)
        if in_currency:
            logger.info(f"Profit/Loss: {win_loss_in_currency} USD.")

        logger.info(f"Profit/Loss: {win_loss} lev.")

    if len(unsupported_activity_types) > 0:
        logger.warning(f"Statements contain unsupported activity types: {unsupported_activity_types}. Only dividends related data was calculated.")