"""Top-level package for le_map_tools."""

__author__ = """Qiusheng Wu"""
__email__ = "giswqs@gmail.com"
__version__ = "0.35.3"

import os


def in_colab_shell():
    """Tests if the code is being executed within Google Colab."""
    import sys

    if "google.colab" in sys.modules:
        return True
    else:
        return False


def use_folium():
    """Whether to use the folium or ipyleaflet plotting backend."""
    if os.environ.get("USE_FOLIUM") is not None:
        return True
    else:
        return False


def _use_eerepr(token="USE_EEREPR"):
    """Whether to use labelearthrepr for printing Earth Engine objects.

    Returns:
        bool: True if labelearthrepr is used for printing Earth Engine objects.
    """

    if os.environ.get(token) is None:
        return True
    else:
        return False


if use_folium():
    from .foliumap import *
else:
    try:
        from .le_map_tools import *
    except Exception as e:
        if in_colab_shell():
            print(
                "Please restart Colab runtime after installation if you encounter any errors when importing le_map_tools."
            )
        else:
            print(
                "Please restart Jupyter kernel after installation if you encounter any errors when importing le_map_tools."
            )
        raise e

if _use_eerepr():
    import labelearthrepr

    labelearthrepr.initialize()

from .report import Report
