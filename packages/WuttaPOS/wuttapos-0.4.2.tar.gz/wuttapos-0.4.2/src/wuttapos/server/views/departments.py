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
Master view for Departments
"""

from wuttaweb.views import MasterView

from wuttapos.db.model import Department, Product


class DepartmentView(MasterView):
    """
    Master view for Departments
    """

    model_class = Department
    model_title = "Department"
    model_title_plural = "Departments"

    route_prefix = "departments"
    url_prefix = "/departments"

    creatable = True
    editable = True
    deletable = True

    labels = {
        "department_id": "Department ID",
    }

    grid_columns = [
        "department_id",
        "name",
        "for_products",
        "for_personnel",
        "exempt_from_gross_sales",
    ]

    form_fields = [
        "department_id",
        "name",
        "for_products",
        "for_personnel",
        "exempt_from_gross_sales",
    ]

    has_rows = True
    row_model_class = Product

    row_grid_columns = [
        "product_id",
        "brand_name",
        "description",
        "size",
        "sold_by_weight",
        "case_size",
        "special_order",
        "unit_price_reg",
    ]

    def configure_grid(self, grid):
        g = grid
        super().configure_grid(g)

        # name
        g.set_link("name")

    def get_row_grid_data(self, obj):
        department = obj
        model = self.app.model
        session = self.app.get_session(department)

        return session.query(model.Product).filter(
            model.Product.department == department
        )

    def configure_row_grid(self, grid):
        g = grid
        super().configure_row_grid(g)

        # links
        g.set_link("product_id")
        g.set_link("brand_name")
        g.set_link("description")
        g.set_link("size")

        # currency
        g.set_renderer("unit_price_reg", "currency")

        # view action
        def view_url(product, i):
            return self.request.route_url("products.view", uuid=product.uuid)

        g.add_action("view", url=view_url, icon="eye")


def defaults(config, **kwargs):
    base = globals()

    DepartmentView = kwargs.get("DepartmentView", base["DepartmentView"])
    DepartmentView.defaults(config)


def includeme(config):
    defaults(config)
