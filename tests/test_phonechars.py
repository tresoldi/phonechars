"""
test_phonechars
===============

Tests for the `phonechars` package.
"""

# Import Python standard libraries
import pytest
from pathlib import Path

# Import the library being tested
import phonechars

TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_copar_full():
    """
    Perform a full COPAR test on a small dataset to check the results.
    """

    # Build input file and run copar main steps
    input_file = str(TEST_DATA_PATH / "fake1.csv")
    source = phonechars.fetch_stream_data(input_file, "utf-8")
    wordlist = phonechars.build_lingpy_matrix(source, "comma")
    chars = phonechars.get_copar_results(wordlist, "cogid")

    pass
