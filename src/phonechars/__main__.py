#!/usr/bin/env python3

"""
__main__.py

Module for command-line extraction of phylogenetic phonological characters.
"""

# TODO: Add support to automatic detection of the delimiter?

# Import Python standard libraries
import argparse
import logging
from pathlib import Path
import csv

# Import our library
import phonechars


def parse_arguments() -> dict:
    """
    Parse command-line arguments and return them as a dictionary.
    """

    parser = argparse.ArgumentParser(
        description="Extract phonological phylogenetic characters from aligned data."
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to the tabular file with the source data. If `-`, will read from stdin.",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default="tab",
        choices=["comma", "tab"],
        help="Delimiter used in the source file. Defaults to `tab`.",
    )
    parser.add_argument(
        "-c",
        "--charfile",
        type=str,
        help="Path to the char file to be generated; if not provided, it will be based on the input filename.",
    )
    parser.add_argument(
        "-r",
        "--corrfile",
        type=str,
        help="Path to the corr file to be generated; if not provided, it will be based on the input filename.",
    )
    parser.add_argument(
        "-n",
        "--nexfile",
        type=str,
        help="Path to the nexus file to be generated; if not provided, it will be based on the input filename.",
    )
    parser.add_argument(
        "-m",
        "--method",
        type=str,
        default="copar",
        choices=["copar"],
        help="The method for extraction to be used.",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=str,
        default="debug",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level.",
    )

    # Get the namespace dictionary, also for web interface compatibility
    runargs = parser.parse_args().__dict__

    return runargs


# TODO: decompose the full `args`, passing only the elements we need?
def run_copar(input_file: str, delimiter: str):
    """
    Runs detection using the CoPAR method.
    """

    # Obtain char information
    source = phonechars.fetch_stream_data(input_file, "utf-8")
    wordlist = phonechars.build_lingpy_matrix(source, delimiter)
    chars = phonechars.get_copar_results(wordlist, "cogid")

    return chars


def obtain_corrs(char_file: str, corr_file: str):
    """
    Extract correspondence phonological characters from a .chars.tsv file.
    """

    # Log and extract base filename
    logging.info(f"Processing `{char_file}`...")

    # Read data
    with open(char_file, encoding="utf-8") as handler:
        char_data = list(csv.DictReader(handler, delimiter="\t"))

    # Extract correspondences
    corr_data = phonechars.chars2corr(char_data)

    # Write to disk
    with open(corr_file, "w", encoding="utf-8") as handler:
        writer = csv.DictWriter(
            handler, delimiter="\t", fieldnames=["DOCULECT", "CHAR", "PHONEME"]
        )
        writer.writeheader()
        writer.writerows(corr_data)

    return corr_data


def main():
    """
    Main function for the `phonechars` command line too.
    """

    # Parse command-line arguments and set the logging level
    args = parse_arguments()
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    logging.basicConfig(level=level_map[args["verbosity"]])

    # Build filenames as needed
    input_file = Path(args["input"])

    if not args["charfile"]:
        char_file = input_file.parent / f"{input_file.stem}.chars.tsv"
    else:
        char_file = Path(args["charfile"])

    if not args["corrfile"]:
        corr_file = input_file.parent / f"{input_file.stem}.corrs.tsv"
    else:
        corr_file = Path(args["corrfile"])

    if not args["nexfile"]:
        nex_file = input_file.parent / f"{input_file.stem}.nex"
    else:
        nex_file = Path(args["nexfile"])

    # Dispatch to the right method for generating .chars.tsv files
    if args["method"] == "copar":
        copar_chars = run_copar(str(input_file), args["delimiter"])
        # Write results to disk; note that we always output TSV files
        # TODO: drop STRUCTURE and other lingpy-only things?
        with open(char_file, "w", encoding="utf-8") as handler:
            writer = csv.DictWriter(
                handler,
                delimiter="\t",
                fieldnames=[
                    "ID",
                    "DOCULECT",
                    "CONCEPT",
                    "IPA",
                    "TOKENS",
                    "COGID",
                    "ALIGNMENT",
                    "STRUCTURE",
                    "PATTERNS",
                ],
            )
            writer.writeheader()
            writer.writerows(copar_chars)
    else:
        raise ValueError(f"Invalid extraction method `{args['method']}`.")

    # Extract correspondences from a .chars.tsv file
    corr_data = obtain_corrs(char_file, corr_file)

    # Build the nexus file from the corr csv file
    nexus_source = phonechars.corrdata2nexus(corr_data)
    with open(nex_file, "w", encoding="utf-8") as handler:
        handler.write(nexus_source)


if __name__ == "__main__":
    main()
