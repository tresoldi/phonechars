"""
Module with functions for handling and exporting NEXUS data.
"""

# Import Python standard libraries
from collections import defaultdict
import csv
import logging


def parse_csv_data(data, taxa):
    """
    Prepare the NEXUS information from a list of dictionaries with the CSV data.

    @param data:
    @param taxa:
    @return:
    """

    # Collect characters
    lang_chars = defaultdict(list)
    all_chars = defaultdict(set)
    for row in data:
        lang_chars[row["DOCULECT"], row["CHAR"]].append(row["PHONEME"])
        all_chars[row["CHAR"]].add(row["PHONEME"])

    all_chars = {key: sorted(value) for key, value in all_chars.items()}

    # Build list of character state and assumptions, including
    # adding ascertainment
    # TODO: make ascertainment optional? allow to have question marks?
    charstates = []
    assumptions = []
    cur_idx = 1
    for cog in sorted(all_chars):
        values = all_chars[cog]

        charstates.append(f"{cog}_ascertainment")
        for value in values:
            charstates.append(f"{cog}_{value}")

        end_idx = cur_idx + len(values)
        assumptions.append([cog, cur_idx, end_idx])
        cur_idx = end_idx + 1

    # Build matrix
    matrix = {}
    for taxon in taxa:
        buf = ""
        for parameter in sorted(all_chars):
            buf += "0"  # ascert
            char_vals = all_chars[parameter]

            # if empty
            if len(lang_chars[taxon, parameter]) == 0:
                buf += "?" * len(char_vals)
            else:
                vector = [char in lang_chars[taxon, parameter] for char in char_vals]
                buf += "".join([["0", "1"][val] for val in vector])

        matrix[taxon] = buf

    return charstates, assumptions, all_chars, matrix


def build_nexus_string(taxa, charstates, assumptions, all_chars, matrix):
    """
    Build the NEXUS string from the parsed information.

    @param taxa:
    @param charstates:
    @param assumptions:
    @param all_chars:
    @param matrix:
    @return:
    """

    taxon_len = max([len(taxon) for taxon in taxa])

    nexus = ""
    nexus += "#NEXUS\n\n"
    nexus += "BEGIN DATA;\n"
    nexus += "\tDIMENSIONS NTAX=%i NCHAR=%i;\n" % (len(taxa), len(matrix[taxa[0]]))
    nexus += '\tFORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="01";'
    nexus += "\tCHARSTATELABELS\n"
    nexus += ",\n".join(
        ["\t\t%i %s" % (idx + 1, cs) for idx, cs in enumerate(charstates)]
    )
    nexus += "\n;\n"
    nexus += "MATRIX\n"
    for taxon, vector in matrix.items():
        label = taxon.ljust(taxon_len + 4)
        nexus += "%s %s\n" % (label, vector)
    nexus += ";\n"
    nexus += "END;\n\n"

    nexus += "BEGIN ASSUMPTIONS;\n"
    for assump in assumptions:
        v = all_chars[assump[0]][0].split("_")[0]
        nexus += "\tcharset %s = %i-%i;\n" % (assump[0], assump[1], assump[2])
    nexus += "END;\n\n"

    return nexus


# TODO: allow output to stdout?
def corrcsv2nexus(corrtsv_file: str, nexus_file: str):
    """
    Read CSV data in the expected format and output a NEXUS file.

    The function takes care of other steps such as adding ascertainment
    correction.

    @param corrcsv_file: Path to the TSV file holding the correspondence information.
    @param nexus_file: Path to the output NEXUS file.
    """

    # Log and extract base filename
    logging.info(f"Processing `{corrtsv_file}`...")

    # Read tsv data
    with open(corrtsv_file, encoding="utf-8") as h:
        data = list(csv.DictReader(h, delimiter="\t"))

    # Get information from CSV data
    taxa = sorted(set([row["DOCULECT"] for row in data]))
    charstates, assumptions, all_chars, matrix = parse_csv_data(data, taxa)

    # Build and write the NEXUS string
    nexus = build_nexus_string(taxa, charstates, assumptions, all_chars, matrix)
    with open(nexus_file, "w", encoding="utf-8") as handler:
        handler.write(nexus)
