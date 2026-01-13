# -*- coding: utf-8; -*-
"""
Master view for Tenders
"""

from wuttapos.db.model.tenders import Tender

from wuttaweb.views import MasterView


class TenderView(MasterView):
    """
    Master view for Tenders
    """

    model_class = Tender
    model_title = "Tender"
    model_title_plural = "Tenders"

    route_prefix = "tenders"
    url_prefix = "/tenders"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "tender_id": "Tender ID",
    }

    grid_columns = [
        "tender_id",
        "name",
        "is_cash",
        "is_foodstamp",
        "allow_cashback",
        "kick_drawer",
        "active",
    ]

    form_fields = [
        "tender_id",
        "name",
        "notes",
        "is_cash",
        "is_foodstamp",
        "allow_cashback",
        "kick_drawer",
        "active",
    ]

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # links
        g.set_link("tender_id")
        g.set_link("name")

    def configure_form(self, form):
        f = form
        super().configure_form(f)

        # notes
        f.set_widget("notes", "notes")


def defaults(config, **kwargs):
    base = globals()

    TenderView = kwargs.get("TenderView", base["TenderView"])
    TenderView.defaults(config)


def includeme(config):
    defaults(config)
