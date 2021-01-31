import glob
import os
from datetime import datetime
import math

from libs import REVOLUT_DATE_FORMAT, REVOLUT_UNSUPPORTED_ACTIVITY_TYPES


def list_statement_files(dir):
    statement_files = []

    if not os.path.exists(dir):
        raise Exception(f"Statement directory[{dir}] doesn't exists.")

    expresion = os.path.join(dir, "**", f"*.pdf")
    for file in glob.glob(expresion, recursive=True):
        if not os.path.isfile(file):
            continue
        statement_files.append(file)

    return statement_files


def humanize_date(list_object):
    result = []
    for elements in list_object:
        item = {}
        for key, value in elements.items():
            if isinstance(value, datetime):
                item[key] = value.strftime(REVOLUT_DATE_FORMAT)
                continue

            item[key] = value

        result.append(item)
    return result


def get_unsupported_activity_types(statements):
    unsupported_activity_types = []
    for statement in statements:
        if statement["activity_type"] in REVOLUT_UNSUPPORTED_ACTIVITY_TYPES:
            unsupported_activity_types.append(statement["activity_type"])

    return list(set(unsupported_activity_types))