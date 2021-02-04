import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytest
import os
import shutil
import glob


test_dir_path = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__":
    pytest.main(args=["-s", test_dir_path, "--disable-warnings", "--log-cli-level=DEBUG", "-x"])  # Debug logging

    # pytest.main(
    #     args=[
    #         "-s",
    #         test_dir_path,
    #         "--disable-warnings",
    #         "--log-cli-level=DEBUG",
    #         "-k",
    #         "selected_test",
    #         "-x",
    #     ]
    # )  # Debug logging and selected tests
