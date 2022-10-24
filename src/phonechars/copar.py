"""
Wrapper to use CoPAR to extract the characters.
"""

# TODO: explore how to make it fully reproductible (set random seeds?)

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

# TODO: make these arguments and not globals
SEGMENTS_FIELD = "SEGMENTS"
CONCEPT_FIELD = "CONCEPT"


def build_lingpy_matrix(
    source: str,
    delimiter: str,
    noid: bool = False,
) -> dict:
    """
    Read a tabular file and build a LingPy matrix from it, as expected by CoPAR.

    @param filename: Path to the source tabular file.
    @param noid: Whether to use the ID field from the original file or a simple
        sequential index. It is recommended to set to `False`, as in some cases
        lingpy and its ecosystem require purely numerical IDs. Defaults to
        `False`.
    @return:
    """

    # Read data and build a dictionary of row indexes to rows, as expected; index 0
    # is the header, so we just skip it here
    delimiter_map = {"comma": ",", "tab": "\t"}
    wordlist = {}
    for idx, entry in enumerate(
        csv.DictReader(io.StringIO(source), delimiter=delimiter_map[delimiter])
    ):
        if noid:
            entry_id = idx + 1
        else:
            entry_id = int(entry["ID"])

        # Grab SEGMENTS and IPA if not available in the source
        segments = entry.get(SEGMENTS_FIELD)
        if not segments:
            segments = entry["ALIGNMENT"].replace("-", "").strip()

        ipa = entry.get("IPA")
        if not ipa:
            ipa = segments.replace(" ", "")

        wordlist[entry_id] = [
            entry["DOCULECT"],
            entry[CONCEPT_FIELD],
            ipa,
            segments,
            entry["COGID"],
            entry["ALIGNMENT"].split(),
        ]

    # Drop entries with a single lemma per cogid (fifth item in the structure, thus [4] -- it is
    # the way lingpy works)
    cogid_count = Counter([entry[4] for _, entry in wordlist.items()])
    entries = [entry for entry in wordlist.values() if cogid_count[entry[4]] > 1]
    wordlist = {idx + 1: entry for idx, entry in enumerate(entries)}

    # Remap all "cogid" fields to the index in the list of cogids (1-based), as we need
    # to address 1. lingpy's requirement for purely numerical indexes and 2. lingrex
    # errors when the cogid is zero
    cogid_map = list(cogid_count.keys())
    for row in wordlist.values():
        row[4] = str(cogid_map.index(row[4]) + 1)

    # Index 0 must hold the header
    wordlist[0] = ["doculect", "concept", "ipa", "tokens", "cogid", "alignment"]

    return wordlist


def get_copar_results(wordlist, refcol):
    """
    Encapsulate CoPAR to run detection.

    Due to the complex internal working of CoPAR and the difficulty in exporting
    the results in-memory, we need to write to a temporary file and read the
    results back, in order to make this more transparent and aligned with the
    intended logic.

    @param wordlist:
    @param refcol:
    @return:
    """

    # Run CoPAR
    # TODO: study CoPAR arguments, might need to pin the lingrex version
    alms = lingpy.Alignments(wordlist, ref=refcol, transcription="ipa")
    lingrex_add_structure(alms, model="cv", structure="structure")
    copar = CoPaR(alms, ref=refcol, structure="structure", minrefs=2)
    copar.get_sites()
    copar.cluster_sites()
    copar.sites_to_pattern()
    copar.add_patterns()
    copar.irregular_patterns()

    # Output to a temporary file, so that we can read back and
    # remove blank lines and comments introduced by lingpy/lingrex; note that
    # the strategy we are using here is not totally safe, as we extract the name
    # and later provide it to copar, but unfortunately we cannot pass a handler directly
    handler = NamedTemporaryFile(mode="w")
    output_file = handler.name
    handler.close()
    copar.output("tsv", filename=output_file)

    # Read back data
    new_lines = []
    headers = None
    with open(f"{output_file}.tsv", encoding="utf-8") as handler:
        for line in handler.readlines():
            line = line.strip()
            if line and line[0] != "#":
                tokens = line.split("\t")
                if not headers:
                    headers = tokens
                else:
                    new_lines.append(
                        {key: value for key, value in zip(headers, tokens)}
                    )

    # Sort values for reproducibility
    new_lines = sorted(new_lines, key=lambda r: (int(r["COGID"]), int(r["ID"])))

    return new_lines
