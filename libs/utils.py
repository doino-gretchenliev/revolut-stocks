import glob
import os
from datetime import datetime
import math

from libs import BNB_DATE_FORMAT


def list_statement_files(dir, file_extension):
    statement_files = []

    if not os.path.exists(dir):
        raise Exception(f"Statement directory[{dir}] doesn't exists.")

    expresion = os.path.join(dir, "**", f"*.{file_extension}")
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
                item[key] = value.strftime(BNB_DATE_FORMAT)
                continue

            item[key] = value

        result.append(item)
    return result
