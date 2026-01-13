# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaPOS -- Point of Sale system based on Wutta Framework
#  Copyright © 2026 Lance Edgar
#
#  This file is part of WuttaPOS.
#
#  WuttaPOS is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  WuttaPOS is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  WuttaPOS.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Master view for Products
"""

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import WuttaQuantity, WuttaMoney

from wuttapos.db.model.products import Product
from wuttapos.server.forms.schema import DepartmentRef


class ProductView(MasterView):
    """
    Master view for Products
    """

    model_class = Product
    model_title = "Product"
    model_title_plural = "Products"

    route_prefix = "products"
    url_prefix = "/products"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "product_id": "Product ID",
    }

    grid_columns = [
        "product_id",
        "brand_name",
        "description",
        "size",
        "sold_by_weight",
        "case_size",
        "department",
        "special_order",
        "unit_price_reg",
    ]

    form_fields = [
        "product_id",
        "brand_name",
        "description",
        "size",
        "department",
        "sold_by_weight",
        "case_size",
        "special_order",
        "unit_cost",
        "unit_price_reg",
        "notes",
        "on_hand",
        "on_order",
    ]

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # links
        g.set_link("product_id")
        g.set_link("brand_name")
        g.set_link("description")
        g.set_link("size")

        # currency
        g.set_renderer("unit_cost", "currency", scale=4)
        g.set_renderer("unit_price_reg", "currency")

    def configure_form(self, form):
        f = form
        super().configure_form(f)
        product = f.model_instance

        # department
        f.set_node("department", DepartmentRef(self.request))

        # case_size
        f.set_node("case_size", WuttaQuantity(self.request))

        # unit_cost
        f.set_node("unit_cost", WuttaMoney(self.request, scale=4))

        # unit_price_reg
        f.set_node("unit_price_reg", WuttaMoney(self.request))

        # notes
        f.set_widget("notes", "notes")

        # on_hand
        f.set_node("on_hand", WuttaQuantity(self.request))
        if self.creating or self.editing:
            f.remove("on_hand")
        else:
            f.set_default(
                "on_hand",
                product.inventory.on_hand if product.inventory else None,
            )

        # on_order
        f.set_node("on_order", WuttaQuantity(self.request))
        if self.creating or self.editing:
            f.remove("on_order")
        else:
            f.set_default(
                "on_order",
                product.inventory.on_order if product.inventory else None,
            )


def defaults(config, **kwargs):
    base = globals()

    ProductView = kwargs.get("ProductView", base["ProductView"])
    ProductView.defaults(config)


def includeme(config):
    defaults(config)
