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
People Handler

This is a :term:`handler` to manage "people" in the DB.
"""

from wuttjamaican import people as base


class PeopleHandler(base.PeopleHandler):
    """
    TODO
    """

    def get_person(self, obj):
        model = self.app.model

        # upstream logic may be good enough
        if person := super().get_person(obj):
            return person

        # employee
        if isinstance(obj, model.Employee):
            employee = obj
            return employee.person

        return None
