"""
coconutPy: A Python wrapper for the COCONUT natural product database REST API.

Classes:
- cocoPy: Main class for interacting with the COCONUT API.
- cocoGet: Class for retrieving resource details from the COCONUT API.
- cocoSearch: Class for performing searches against COCONUT database.
- cocoAdvSearch: Class for performing advanced searches against COCONUT database.
- cocoLog: Class for logging in to the COCONUT API.
"""

from .cocoPy import cocoPy

__all__ = ["cocoPy"]