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
Common views
"""

from wuttaweb.views import common as base


class CommonView(base.CommonView):
    """
    Common views
    """

    def setup_enhance_admin_user(self, user):
        """ """
        model = self.app.model
        session = self.app.get_session(user)
        auth = self.app.get_auth_handler()

        site_admin = session.query(model.Role).filter_by(name="Site Admin").first()
        if site_admin:
            site_admin_perms = [
                "batch.pos.list",
                "batch.pos.view",
                "customers.list",
                "customers.create",
                "customers.view",
                "customers.edit",
                "departments.list",
                "departments.create",
                "departments.view",
                "departments.edit",
                "employees.list",
                "employees.create",
                "employees.view",
                "employees.edit",
                "inventory_adjustment_types.list",
                "inventory_adjustment_types.create",
                "inventory_adjustment_types.view",
                "inventory_adjustment_types.edit",
                "inventory_adjustments.list",
                "inventory_adjustments.create",
                "inventory_adjustments.view",
                "pos.test_error",
                "pos.ring_sales",
                "pos.override_price",
                "pos.del_customer",
                "pos.toggle_training",
                "pos.suspend",
                "pos.swap_customer",
                "pos.void_txn",
                "products.list",
                "products.create",
                "products.view",
                "products.edit",
                "stores.list",
                "stores.create",
                "stores.view",
                "stores.edit",
                "taxes.list",
                "taxes.create",
                "taxes.view",
                "taxes.edit",
                "tenders.list",
                "tenders.create",
                "tenders.view",
                "tenders.edit",
                "terminals.list",
                "terminals.create",
                "terminals.view",
                "terminals.edit",
            ]
            for perm in site_admin_perms:
                auth.grant_permission(site_admin, perm)


def defaults(config, **kwargs):
    local = globals()
    CommonView = kwargs.get("CommonView", local["CommonView"])
    base.defaults(config, **{"CommonView": CommonView})


def includeme(config):
    defaults(config)
