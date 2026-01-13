# -*- coding: utf-8; -*-
"""
Master view for Taxes
"""

from wuttapos.db.model.taxes import Tax

from wuttaweb.views import MasterView


class TaxView(MasterView):
    """
    Master view for Taxes
    """

    model_class = Tax
    model_title = "Tax"
    model_title_plural = "Taxes"

    route_prefix = "taxes"
    url_prefix = "/taxes"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "tax_id": "Tax ID",
    }

    grid_columns = [
        "tax_id",
        "name",
        "rate",
    ]

    form_fields = [
        "tax_id",
        "name",
        "rate",
    ]


def defaults(config, **kwargs):
    base = globals()

    TaxView = kwargs.get("TaxView", base["TaxView"])
    TaxView.defaults(config)


def includeme(config):
    defaults(config)
