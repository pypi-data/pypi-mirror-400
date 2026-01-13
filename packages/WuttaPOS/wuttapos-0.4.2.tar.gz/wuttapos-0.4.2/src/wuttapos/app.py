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
WuttaPOS app
"""

from wuttjamaican import app as base


class WuttaPosAppHandler(base.AppHandler):
    """
    Custom :term:`app handler` for WuttaPOS.
    """

    default_people_handler_spec = "wuttapos.people:PeopleHandler"
    default_employment_handler_spec = "wuttapos.employment:EmploymentHandler"
    default_clientele_handler_spec = "wuttapos.clientele:ClienteleHandler"
    default_products_handler_spec = "wuttapos.products:ProductsHandler"
    default_install_handler_spec = "wuttapos.install:InstallHandler"

    def get_clientele_handler(self):
        """
        Get the configured "clientele" :term:`handler`.

        :rtype: :class:`~wuttapos.clientele.ClienteleHandler`
        """
        if "clientele" not in self.app.handlers:
            spec = self.config.get(
                f"{self.appname}.clientele.handler",
                default=self.default_clientele_handler_spec,
            )
            factory = self.app.load_object(spec)
            self.app.handlers["clientele"] = factory(self.config)
        return self.app.handlers["clientele"]

    def get_employment_handler(self):
        """
        Get the configured "employment" :term:`handler`.

        :rtype: :class:`~wuttapos.employment.EmploymentHandler`
        """
        if "employment" not in self.app.handlers:
            spec = self.config.get(
                f"{self.appname}.employment.handler",
                default=self.default_employment_handler_spec,
            )
            factory = self.app.load_object(spec)
            self.app.handlers["employment"] = factory(self.config)
        return self.app.handlers["employment"]

    def get_products_handler(self):
        """
        Get the configured "products" :term:`handler`.

        :rtype: :class:`~wuttapos.products.ProductsHandler`
        """
        if "products" not in self.app.handlers:
            spec = self.config.get(
                f"{self.appname}.products.handler",
                default=self.default_products_handler_spec,
            )
            factory = self.app.load_object(spec)
            self.app.handlers["products"] = factory(self.config)
        return self.app.handlers["products"]

    def get_employee(self, obj):
        """
        Convenience method to locate a
        :class:`~wuttjamaican.db.model.base.Person` for the given
        object.

        This delegates to the "people" handler method,
        :meth:`~wuttjamaican.people.PeopleHandler.get_person()`.
        """
        return self.get_employment_handler().get_employee(obj)


class WuttaPosAppProvider(base.AppProvider):
    """
    Custom :term:`app provider` for WuttaPOS.
    """

    email_templates = ["wuttapos:email-templates"]
