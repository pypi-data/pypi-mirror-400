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
WuttaPOS - item lookup for department
"""

from .itemlookup import WuttaProductLookup


class WuttaProductLookupByDepartment(WuttaProductLookup):

    def __init__(self, config, department, *args, **kwargs):

        # nb. this forces first query
        kwargs.setdefault("initial_search", True)

        kwargs.setdefault("show_search", False)

        super().__init__(config, *args, **kwargs)
        model = self.app.model

        if isinstance(department, model.Department):
            self.department_key = department.uuid
        else:
            self.department_key = department

    # TODO: should somehow combine these 2 approaches, so the user can
    # still filter items within a department

    # def get_results(self, session, entry):
    #     return self.app.get_products_handler().search_products(session, entry)

    def get_results(self, session, entry):
        org = self.app.get_org_handler()
        prod = self.app.get_products_handler()
        model = self.app.model

        department = org.get_department(session, self.department_key)
        if not department:
            raise ValueError(f"department not found: {self.department_key}")

        products = (
            session.query(model.Product)
            .filter(model.Product.department == department)
            .all()
        )

        products = [prod.normalize_product(p) for p in products]

        return products
