"""
phonechars __init__.py
"""

# Version of the phonechars package
__version__ = "0.1"  # Remember to sync with setup.py
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

# Import from local modules
from .common import dummy

# Build the namespace
__all__ = [
    "dummy",
]
