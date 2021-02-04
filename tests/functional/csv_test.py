import pytest
import os
from libs.process import process

from csv_diff import load_csv, compare

from lxml import etree
from xmldiff import main


@pytest.fixture(scope="session")
def tmp_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("test")


def assert_csv_diff(diff):
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["changed"] == []
    assert diff["columns_added"] == []
    assert diff["columns_removed"] == []


def test_csv_generation(tmp_dir):
    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
    input_dir = os.path.join(resources_dir, "input")
    golden_dir = os.path.join(resources_dir, "golden")
    # output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")  # For debugging purposes
    output_dir = tmp_dir

    input_statements_csv = load_csv(open(os.path.join(input_dir, "test.csv")))
    process(input_dir, output_dir, "csv", False)

    output_statements_csv = load_csv(open(os.path.join(output_dir, "statements.csv")))

    diff = compare(input_statements_csv, output_statements_csv)
    assert_csv_diff(diff)

    golden = load_csv(open(os.path.join(golden_dir, "app8-part4-1.csv")))
    output = load_csv(open(os.path.join(output_dir, "app8-part4-1.csv")))

    diff = compare(golden, output)
    assert_csv_diff(diff)

    golden = load_csv(open(os.path.join(golden_dir, "app8-part1.csv")))
    output = load_csv(open(os.path.join(output_dir, "app8-part1.csv")))

    diff = compare(golden, output)
    assert_csv_diff(diff)

    golden = load_csv(open(os.path.join(golden_dir, "app5-table2.csv")))
    output = load_csv(open(os.path.join(output_dir, "app5-table2.csv")))

    diff = compare(golden, output)
    assert_csv_diff(diff)

    golden = os.path.join(golden_dir, "dec50_2020_data.xml")
    output = os.path.join(output_dir, "dec50_2020_data.xml")

    assert len(main.diff_files(golden, output)) == 0
