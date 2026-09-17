"""
HydroFed-ICAF: CDSS Streamlit Application Entry Wrapper.
Delegates cleanly to the root app entry point.
"""

import os
import sys

# Ensure root workspace is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import app
