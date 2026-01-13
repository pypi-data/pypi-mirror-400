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
WuttaPOS - department lookup control
"""

from .lookup import WuttaLookup


class WuttaDepartmentLookup(WuttaLookup):

    def __init__(self, *args, **kwargs):

        # nb. this forces first query
        kwargs.setdefault("initial_search", "")
        kwargs.setdefault("allow_empty_query", True)

        super().__init__(*args, **kwargs)

    def get_results_columns(self):
        return [
            "Department ID",
            "Name",
        ]

    def get_results(self, session, entry):
        model = self.app.model
        query = session.query(model.Department).order_by(model.Department.name)

        if entry:
            query = query.filter(model.Department.name.ilike(f"%{entry}%"))

        departments = []
        for dept in query:
            departments.append(
                {
                    "uuid": dept.uuid,
                    "department_id": dept.department_id,
                    "name": dept.name,
                }
            )
        return departments

    def make_result_row(self, dept):
        return [
            dept["department_id"],
            dept["name"],
        ]
