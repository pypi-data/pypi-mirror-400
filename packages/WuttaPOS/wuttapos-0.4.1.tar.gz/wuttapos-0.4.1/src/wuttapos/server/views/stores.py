# -*- coding: utf-8; -*-
"""
Master view for Stores
"""

from wuttapos.db.model.stores import Store

from wuttaweb.views import MasterView


class StoreView(MasterView):
    """
    Master view for Stores
    """

    model_class = Store
    model_title = "Store"
    model_title_plural = "Stores"

    route_prefix = "stores"
    url_prefix = "/stores"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "store_id": "Store ID",
    }

    grid_columns = [
        "store_id",
        "name",
        "active",
    ]

    form_fields = [
        "store_id",
        "name",
        "active",
    ]


def defaults(config, **kwargs):
    base = globals()

    StoreView = kwargs.get("StoreView", base["StoreView"])
    StoreView.defaults(config)


def includeme(config):
    defaults(config)
