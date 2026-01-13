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
Master view for Inventory Adjustments
"""

from collections import OrderedDict

from wuttaweb.views import MasterView
from wuttaweb.forms import widgets
from wuttaweb.forms.schema import WuttaQuantity

from wuttapos.db.model.products import (
    InventoryAdjustment,
    InventoryAdjustmentType,
)
from wuttapos.server.forms.schema import ProductRef, InventoryAdjustmentTypeRef


def render_grid_product(adjustment, field, value):
    product = adjustment.inventory.product
    return str(product)


class InventoryAdjustmentTypeView(MasterView):
    """
    Master view for Inventory Adjustment Types
    """

    model_class = InventoryAdjustmentType
    model_title = "Inventory Adjustment Type"
    model_title_plural = "Inventory Adjustment Types"

    route_prefix = "inventory_adjustment_types"
    url_prefix = "/inventory/adjustment-types"

    creatable = True
    editable = True
    deletable = True

    grid_columns = [
        "type_code",
        "name",
    ]

    form_fields = [
        "type_code",
        "name",
    ]

    has_rows = True
    row_model_class = InventoryAdjustment
    row_model_title_plural = "Inventory Adjustments"

    row_grid_columns = [
        "product",
        "adjusted",
        "effective_date",
        "adjustment_type",
        "amount",
        "source",
    ]

    rows_sort_defaults = ("adjusted", "desc")

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # links
        g.set_link("type_code")
        g.set_link("name")

    def get_row_grid_data(self, obj):
        adjustment_type = obj
        model = self.app.model
        session = self.app.get_session(adjustment_type)

        return session.query(model.InventoryAdjustment).filter(
            model.InventoryAdjustment.adjustment_type == adjustment_type
        )

    def configure_row_grid(self, grid):
        g = grid
        super().configure_row_grid(g)
        model = self.app.model
        session = self.Session()

        # product
        g.set_renderer("product", render_grid_product)
        g.set_link("product")

        # view action
        def view_url(adjustment, i):
            return self.request.route_url(
                "inventory_adjustments.view", uuid=adjustment.uuid
            )

        g.add_action("view", url=view_url, icon="eye")


class InventoryAdjustmentView(MasterView):
    """
    Master view for Inventory Adjustments
    """

    model_class = InventoryAdjustment
    model_title = "Inventory Adjustment"
    model_title_plural = "Inventory Adjustments"

    route_prefix = "inventory_adjustments"
    url_prefix = "/inventory/adjustments"

    creatable = True
    editable = False
    deletable = False

    grid_columns = [
        "product",
        "adjusted",
        "effective_date",
        "adjustment_type",
        "amount",
        "source",
    ]

    form_fields = [
        "product",
        "effective_date",
        "adjusted",
        "adjustment_type",
        "amount",
        "source",
    ]

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)
        model = self.app.model
        session = self.Session()

        # product
        g.set_renderer("product", render_grid_product)
        g.set_link("product")

        # adjustment_type
        g.set_joiner(
            "adjustment_type",
            lambda q: q.outerjoin(
                model.InventoryAdjustmentType,
                model.InventoryAdjustmentType.type_code
                == self.model_class.adjustment_type_code,
            ),
        )
        g.set_sorter("adjustment_type", model.InventoryAdjustmentType.name)
        g.remove_filter("adjustment_type_code")
        types = session.query(model.InventoryAdjustmentType).order_by(
            model.InventoryAdjustmentType.name
        )
        choices = OrderedDict([(typ.type_code, typ.name) for typ in types])
        g.set_filter(
            "adjustment_type",
            model.InventoryAdjustmentType.type_code,
            verbs=["equal", "not_equal"],
            choices=choices,
        )

    def configure_form(self, form):
        f = form
        super().configure_form(f)
        model = self.app.model
        session = self.Session()
        adjustment = f.model_instance

        # product
        f.set_node("product", ProductRef(self.request))
        if self.creating:
            if uuid := self.request.GET.get("product"):
                if product := session.get(model.Product, uuid):
                    f.set_default("product", product)
                    f.fields.insert_after("product", "on_hand")
                    f.set_node("on_hand", WuttaQuantity(self.request))
                    f.set_readonly("on_hand")
                    f.set_default(
                        "on_hand",
                        product.inventory.on_hand if product.inventory else None,
                    )
        else:
            f.set_default("product", adjustment.inventory.product)

        # adjustment_type
        f.set_node(
            "adjustment_type",
            InventoryAdjustmentTypeRef(self.request, empty_option=True),
        )
        f.set_required("adjustment_type", False)

        # adjusted
        if self.creating:
            f.remove("adjusted")

        # effective_date
        if self.creating:
            f.remove("effective_date")

        # amount
        f.set_node("amount", WuttaQuantity(self.request))

    def objectify(self, form):
        model = self.app.model
        adjustment = super().objectify(form)

        if self.creating:

            inventory = form.validated["product"].inventory
            if not inventory:
                inventory = model.ProductInventory(product=form.validated["product"])

            adjustment.inventory = inventory
            adjustment.adjusted = self.app.make_utc()
            adjustment.effective_date = self.app.localtime().date()

            if adjustment.adjustment_type == -99:
                adjustment.adjustment_type = None

            inventory.on_hand = (inventory.on_hand or 0) + adjustment.amount

        return adjustment


def defaults(config, **kwargs):
    base = globals()

    InventoryAdjustmentTypeView = kwargs.get(
        "InventoryAdjustmentTypeView", base["InventoryAdjustmentTypeView"]
    )
    InventoryAdjustmentTypeView.defaults(config)

    InventoryAdjustmentView = kwargs.get(
        "InventoryAdjustmentView", base["InventoryAdjustmentView"]
    )
    InventoryAdjustmentView.defaults(config)


def includeme(config):
    defaults(config)
