#!/usr/bin/env python3

"""
__main__.py

Module for command-line extraction of phylogenetic phonological characters.
"""

# Import Python standard libraries
import argparse

# Import our library
import phonechars


def parse_arguments():
    """
    Parses arguments and returns a namespace.

    :return: A namespace with all the parameters.
    """

    args = {}

    return args


def main():
    """
    Main function for the `phonechars` command line too.
    """

    # Parse command-line arguments
    args = parse_arguments()

    print("args", args)
    print(phonechars.dummy())


if __name__ == "__main__":
    main()
