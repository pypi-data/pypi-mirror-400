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
Model for Departments
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Department(model.Base):
    """
    Represents an organizational department, for products and/or personnel.
    """

    __tablename__ = "department"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Department",
        "model_title_plural": "Departments",
    }

    uuid = model.uuid_column()

    department_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for the department.
        """,
    )

    name = sa.Column(
        sa.String(length=100),
        nullable=False,
        doc="""
        Name of the department.
        """,
    )

    for_products = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates the department exists to organize products.
        """,
    )

    for_personnel = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates the department exists to organize personnel.
        """,
    )

    exempt_from_gross_sales = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
        Indicates products in this department do not count toward gross sales.
        """,
    )

    def __str__(self):
        return self.name or ""
