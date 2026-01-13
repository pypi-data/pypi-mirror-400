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
Master view for POS Batches
"""

from wuttaweb.views.batch import BatchMasterView

from wuttapos.db.model import POSBatch
from wuttapos.server.forms.schema import StoreRef, TerminalRef, EmployeeRef, CustomerRef


class POSBatchView(BatchMasterView):
    """
    Master view for POS Batches
    """

    model_class = POSBatch

    route_prefix = "batch.pos"
    url_prefix = "/batch/pos"

    creatable = False
    editable = False
    # nb. allow delete for now, at least is useful in dev?
    deletable = True
    executable = False

    labels = {
        "terminal_id": "Terminal ID",
    }

    grid_columns = [
        "id",
        "created",
        "store",
        "terminal",
        "cashier",
        "customer",
        "row_count",
        "sales_total",
        "void",
        "training_mode",
        "status_code",
        "executed",
    ]

    form_fields = [
        "id",
        "terminal",
        "cashier",
        "customer",
        "customer_is_member",
        "customer_is_employee",
        "params",
        "row_count",
        "sales_total",
        # 'taxes',
        "tender_total",
        "fs_tender_total",
        "balance",
        "void",
        "training_mode",
        "status_code",
        "created",
        "created_by",
        "executed",
        "executed_by",
    ]

    filter_defaults = {
        "executed": {"active": True, "verb": "is_null"},
    }

    row_grid_columns = [
        "sequence",
        "row_type",
        "item_entry",
        "description",
        "product",
        "reg_price",
        "txn_price",
        "quantity",
        "sales_total",
        "tender_total",
        "tax_code",
        "modified_by",
    ]

    def get_batch_handler(self):
        """
        Must return the :term:`batch handler` for use with this view.

        There is no default logic; subclass must override.
        """
        spec = "wuttapos.batch.pos:POSBatchHandler"
        factory = self.app.load_object(spec)
        return factory(self.config)

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # links
        g.set_link("terminal")
        g.set_link("cashier")
        g.set_link("customer")

    def grid_row_class(self, batch, data, i):
        if batch.training_mode:
            return "has-background-warning"
        if batch.void:
            return "has-background-danger-light"
        return None

    def configure_form(self, form):
        f = form
        super().configure_form(f)

        # store
        f.set_node("store", StoreRef(self.request))

        # terminal
        f.set_node("terminal", TerminalRef(self.request))

        # cashier
        f.set_node("cashier", EmployeeRef(self.request))

        # customer
        f.set_node("customer", CustomerRef(self.request))


def defaults(config, **kwargs):
    base = globals()

    POSBatchView = kwargs.get("POSBatchView", base["POSBatchView"])
    POSBatchView.defaults(config)


def includeme(config):
    defaults(config)
