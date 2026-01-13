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
WuttaPOS server menu
"""

from wuttaweb import menus as base


class WuttaPosMenuHandler(base.MenuHandler):
    """
    WuttaPOS menu handler
    """

    def make_menus(self, request, **kwargs):
        return [
            self.make_people_menu(request),
            self.make_products_menu(request),
            self.make_batches_menu(request),
            self.make_admin_menu(request),
        ]

    def make_people_menu(self, request):
        return {
            "title": "People",
            "type": "menu",
            "items": [
                {
                    "title": "Customers",
                    "route": "customers",
                    "perm": "customers.list",
                },
                {
                    "title": "Employees",
                    "route": "employees",
                    "perm": "employees.list",
                },
                {
                    "title": "All People",
                    "route": "people",
                    "perm": "people.list",
                },
            ],
        }

    def make_products_menu(self, request):
        return {
            "title": "Products",
            "type": "menu",
            "items": [
                {
                    "title": "Products",
                    "route": "products",
                    "perm": "products.list",
                },
                {"type": "sep"},
                {
                    "title": "Departments",
                    "route": "departments",
                    "perm": "departments.list",
                },
                {"type": "sep"},
                {
                    "title": "Inventory Adjustments",
                    "route": "inventory_adjustments",
                    "perm": "inventory_adjustments.list",
                },
                {
                    "title": "New Inventory Adjustment",
                    "route": "inventory_adjustments.create",
                    "perm": "inventory_adjustments.create",
                },
                {
                    "title": "Inventory Adjustment Types",
                    "route": "inventory_adjustment_types",
                    "perm": "inventory_adjustment_types.list",
                },
                # {
                #     "title": "Vendors",
                #     "route": "vendors",
                #     "perm": "vendors.list",
                # },
            ],
        }

    def make_batches_menu(self, request):
        return {
            "title": "Batches",
            "type": "menu",
            "items": [
                {
                    "title": "POS",
                    "route": "batch.pos",
                    "perm": "batch.pos.list",
                },
            ],
        }

    def make_admin_menu(self, request, **kwargs):
        kwargs.setdefault("include_people", False)
        menu = super().make_admin_menu(request, **kwargs)

        menu["items"] = [
            {
                "title": "Stores",
                "route": "stores",
                "perm": "stores.list",
            },
            {
                "title": "Terminals",
                "route": "terminals",
                "perm": "terminals.list",
            },
            {
                "title": "Tenders",
                "route": "tenders",
                "perm": "tenders.list",
            },
            {
                "title": "Taxes",
                "route": "taxes",
                "perm": "taxes.list",
            },
            {"type": "sep"},
        ] + menu["items"]

        return menu
