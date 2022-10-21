"""
phonechars __init__.py
"""

# Version of the phonechars package
__version__ = "0.1"  # Remember to sync with setup.py
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

# Import from local modules
from .common import dummy, fetch_stream_data, chars2corr
from .copar import build_lingpy_matrix, get_copar_results
from .ipa import ipa2xsampa
from .nexus import corrcsv2nexus

# Build the namespace
__all__ = [
    "dummy",
    "build_lingpy_matrix",
    "get_copar_results",
    "ipa2xsampa",
    "chars2corr",
]
