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
Employment handler
"""

from wuttjamaican.app import GenericHandler


class EmploymentHandler(GenericHandler):
    """
    Base class and default implementation for employment handlers.
    """

    def get_employee(self, obj):
        """
        Returns the Employee associated with the given object, if any.
        """
        model = self.app.model

        if isinstance(obj, model.Employee):
            employee = obj
            return employee

        if person := self.app.get_person(obj):
            if person.employee:
                return person.employee

        return None

    # def make_employee(self, person):
    #     """
    #     Create and return a new employee record.
    #     """
    #     employee = self.model.Employee()
    #     employee.person = person
    #     return employee
