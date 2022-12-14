"""
test_phonechars
===============

Tests for the `phonechars` package.
"""

# Import Python standard libraries
from multiprocessing.context import assert_spawning
import hashlib
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
    char_data = phonechars.get_copar_results(wordlist, "cogid")

    # Test character extraction
    assert len(char_data) == 18
    assert (char_data[0]["ID"], char_data[0]["DOCULECT"], char_data[0]["CONCEPT"]) == (
        "1",
        "LANG_A",
        "FIRE",
    )
    assert (char_data[13]["STRUCTURE"], char_data[13]["PATTERNS"]) == (
        "c v v c v",
        "1-2/f 2-2/a 3-2/i 4-3/r 7-2/e",
    )

    # Test correspondence extraction
    corr_data = phonechars.chars2corr(char_data)
    assert len(corr_data) == 41
    assert (
        corr_data[9]["DOCULECT"],
        corr_data[9]["CHAR"],
        corr_data[9]["PHONEME"],
    ) == ("LANG_E", "c2_2", "a")
    assert (
        corr_data[40]["DOCULECT"],
        corr_data[40]["CHAR"],
        corr_data[40]["PHONEME"],
    ) == ("LANG_D", "c9_1", "!y")

    # Test NEXUS generation
    # TODO: better test for nexus output?
    nexus_source = phonechars.corrdata2nexus(corr_data)
    assert len(nexus_source) == 1016
    m = hashlib.sha256()
    m.update(nexus_source.encode("utf-8"))
    assert (
        m.hexdigest()
        == "b4364c18ebe91f4eae01d024cf9dfa50132b3853bd7aa451ee3bab64db3b9c87"
    )
