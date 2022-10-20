#!/usr/bin/env python3

"""
__main__.py

Module for command-line extraction of phylogenetic phonological characters.
"""

# TODO: Add support to automatic detection of the delimiter?

# Import Python standard libraries
import argparse
import logging

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
        "input", type=str, help="Path to the tabular file with the source data. If `-`, will read from stdin."
    )
    parser.add_argument(
        "-d", "--delimiter", type=str,
        default="tab",
        choices=["comma", "tab"],
        help="Delimiter used in the source file. Defaults to `tab`."
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


def run_copar(args: dict):
    """
    Runs detection using the CoPAR method.

    :param args: Command-line arguments for the extraction.
    """

    source = phonechars.fetch_stream_data(args["input"], "utf-8")
    D = phonechars.build_lingpy_matrix(source, args["delimiter"])
    chars = phonechars.get_copar_results(D, "cogid")

    print(chars[:3])


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

    # Dispatch to the right method
    if args["method"] == "copar":
        run_copar(args)
    else:
        raise ValueError(f"Invalid extraction method `{args['method']}`.")


if __name__ == "__main__":
    main()
