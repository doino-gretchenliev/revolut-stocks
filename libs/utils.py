import glob
import os
from datetime import datetime
import math

from libs import REVOLUT_DATE_FORMAT


def list_statement_files(dir):
    statement_files = []

    if not os.path.exists(dir):
        raise Exception(f"Statement directory[{dir}] doesn't exists.")

    expresion_pdf = os.path.join(dir, "**", f"*.pdf")
    expresion_csv = os.path.join(dir, "**", f"*.csv")

    for file in glob.glob(expresion_pdf, recursive=True) + glob.glob(expresion_csv, recursive=True):
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
