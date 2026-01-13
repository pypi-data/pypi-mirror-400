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
WuttaPOS server views
"""

from wuttaweb.views import essential


def includeme(config):

    # wuttaweb
    essential.defaults(
        config,
        **{
            "wuttaweb.views.common": "wuttapos.server.views.common",
            "wuttaweb.views.settings": "wuttapos.server.views.settings",
        }
    )

    # wuttapos
    config.include("wuttapos.server.views.stores")
    config.include("wuttapos.server.views.terminals")
    config.include("wuttapos.server.views.employees")
    config.include("wuttapos.server.views.tenders")
    config.include("wuttapos.server.views.taxes")
    config.include("wuttapos.server.views.departments")
    config.include("wuttapos.server.views.products")
    config.include("wuttapos.server.views.inventory_adjustments")
    config.include("wuttapos.server.views.customers")
    config.include("wuttapos.server.views.batch.pos")

    # TODO: these should probably live elsewhere?
    config.add_wutta_permission_group("pos", "POS", overwrite=False)

    config.add_wutta_permission(
        "pos", "pos.test_error", "Force error to test error handling"
    )
    config.add_wutta_permission(
        "pos", "pos.ring_sales", "Make transactions (ring sales)"
    )
    config.add_wutta_permission(
        "pos", "pos.override_price", "Override price for any item"
    )
    config.add_wutta_permission(
        "pos", "pos.del_customer", "Remove customer from current transaction"
    )
    # config.add_wutta_permission('pos', 'pos.resume',
    #                                "Resume previously-suspended transaction")
    config.add_wutta_permission("pos", "pos.toggle_training", "Start/end training mode")
    config.add_wutta_permission("pos", "pos.suspend", "Suspend current transaction")
    config.add_wutta_permission(
        "pos", "pos.swap_customer", "Swap customer for current transaction"
    )
    config.add_wutta_permission("pos", "pos.void_txn", "Void current transaction")
