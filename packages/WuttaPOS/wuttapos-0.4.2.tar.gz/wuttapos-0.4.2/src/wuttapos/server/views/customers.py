# -*- coding: utf-8; -*-
"""
Master view for Customers
"""

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import PersonRef

from wuttapos.db.model.customers import Customer


class CustomerView(MasterView):
    """
    Master view for Customers
    """

    model_class = Customer
    model_title = "Customer"
    model_title_plural = "Customers"

    route_prefix = "customers"
    url_prefix = "/customers"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "customer_id": "Customer ID",
    }

    grid_columns = [
        "customer_id",
        "name",
        "phone_number",
        "email_address",
    ]

    form_fields = [
        "customer_id",
        "name",
        "account_holder",
        "phone_number",
        "email_address",
    ]

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # links
        g.set_link("customer_id")
        g.set_link("name")

    def configure_form(self, form):
        f = form
        super().configure_form(f)

        # account_holder
        f.set_node("account_holder", PersonRef(self.request))
        f.set_required("account_holder", False)


def defaults(config, **kwargs):
    base = globals()

    CustomerView = kwargs.get("CustomerView", base["CustomerView"])
    CustomerView.defaults(config)


def includeme(config):
    defaults(config)
