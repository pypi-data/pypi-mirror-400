"""Module for reporting issues with le_map_tools."""

# *******************************************************************************#
# This module contains extra features of the le_map_tools package.                     #
# The le_map_tools community will maintain the extra features.                         #
# *******************************************************************************#

import scooby
from typing import Optional


class Report(scooby.Report):
    def __init__(
        self,
        additional: Optional[dict] = None,
        ncol: int = 3,
        text_width: int = 80,
        sort: bool = False,
    ):
        """Initiate a scooby.Report instance."""
        core = [
            "le_map_tools",
            "ee",
            "ipyleaflet",
            "folium",
            "jupyterlab",
            "notebook",
            "ipyevents",
        ]
        optional = ["geopandas", "localtileserver"]

        scooby.Report.__init__(
            self,
            additional=additional,
            core=core,
            optional=optional,
            ncol=ncol,
            text_width=text_width,
            sort=sort,
        )
