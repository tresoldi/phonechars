"""
Wrapper to use CoPAR to extract the characters.
"""

# Import Python standard libraries
import logging
import csv
from collections import Counter
import io
from tempfile import NamedTemporaryFile

# Import 3rd-party libraries
import lingpy
from lingrex.copar import CoPaR
from lingrex.util import add_structure as lingrex_add_structure

# Import local modules
from . import common

SEGMENTS_FIELD = "SEGMENTS"
CONCEPT_FIELD = "CONCEPT"


def build_lingpy_matrix(
    source: str,
    delimiter: str,
    encoding="utf-8",
    noid: bool = False,
    noipa: bool = False,
) -> dict:
    """
    Read a tabular file and build a LingPy matrix from it, as expected by CoPAR.

    :param filename: Path to the source tabular file.
    :param noid: Whether to use the ID field from the original file or a simple
        sequential index. It is recommended to set to `False`, as in some cases
        lingpy and its ecosystem require purely numerical IDs. Defaults to
        `False`.
    :param noipa: Whether to carry an "IPA" field from the source or to
        build it using the provided segments. Note that this is not used in
        the extraction, but it is a requirement from the lingpy ecosystem.
        Defaults to `False`.
    :return:
    """

    del_map = {"comma": ",", "tab": "\t"}
    D = {0: ["doculect", "concept", "ipa", "tokens", "cogid", "alignment"]}
    for idx, entry in enumerate(
        csv.DictReader(io.StringIO(source), delimiter=del_map[delimiter])
    ):
        if noid:
            entry_id = idx + 1
        else:
            entry_id = int(entry["ID"])

        if noipa:
            ipa = entry[SEGMENTS_FIELD].replace(" ", "")
        else:
            ipa = entry["IPA"]

        D[entry_id] = [
            entry["DOCULECT"],
            entry[CONCEPT_FIELD],
            ipa,
            entry[SEGMENTS_FIELD],
            entry["COGID"],
            entry["ALIGNMENT"].split(),
        ]

    # Drop entries with a single lemma per cogid; note that this will not
    # account for the first one
    cogid_count = Counter([entry[4] for idx, entry in D.items()])
    drops = []
    entries = [entry for entry in D.values() if cogid_count[entry[4]] > 1]
    entries = [entry for entry in entries if entry[4] not in drops]
    D = {idx + 1: entry for idx, entry in enumerate(entries)}
    D[0] = ["doculect", "concept", "ipa", "tokens", "cogid", "alignment"]

    return D


def get_copar_results(D, refcol):
    """
    Encapsulate CoPAR to run detection.

    Due to the complex internal working of CoPAR and the difficulty in exporting
    the results in-memory, we need to write to a temporary file and read the
    results back, in order to make this more transparent and aligned with the
    intended logic.
    """

    alms = lingpy.Alignments(D, ref=refcol, transcription="ipa")
    lingrex_add_structure(alms, model="cv", structure="structure")
    cp = CoPaR(alms, ref=refcol, structure="structure", minrefs=2)
    cp.get_sites()
    cp.cluster_sites()
    cp.sites_to_pattern()
    cp.add_patterns()
    cp.irregular_patterns()

    # Output to a temporary file, so that we can read back and
    # remove blank lines and comments introduced by lingpy/lingrex
    handler = NamedTemporaryFile(mode="w")
    output_file = handler.name
    handler.close()
    cp.output("tsv", filename=output_file)

    # Read back data
    new_lines = []
    headers = None
    with open(f"{output_file}.tsv", encoding="utf-8") as handler:
        for line in handler.readlines():
            line = line.strip()
            if line and line[0] != "#":
                if not headers:
                    headers = line.split("\t")
                else:
                    new_lines.append(
                        {key: value for key, value in zip(headers, line.split("\t"))}
                    )

    return new_lines
