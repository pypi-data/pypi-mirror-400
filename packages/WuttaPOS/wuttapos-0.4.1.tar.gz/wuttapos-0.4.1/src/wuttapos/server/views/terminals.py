# -*- coding: utf-8; -*-
"""
Master view for Terminals
"""

from wuttapos.db.model.terminals import Terminal

from wuttaweb.views import MasterView


class TerminalView(MasterView):
    """
    Master view for Terminals
    """

    model_class = Terminal
    model_title = "Terminal"
    model_title_plural = "Terminals"

    route_prefix = "terminals"
    url_prefix = "/terminals"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "terminal_id": "Terminal ID",
    }

    grid_columns = [
        "terminal_id",
        "name",
    ]

    form_fields = [
        "terminal_id",
        "name",
    ]


def defaults(config, **kwargs):
    base = globals()

    TerminalView = kwargs.get("TerminalView", base["TerminalView"])
    TerminalView.defaults(config)


def includeme(config):
    defaults(config)
