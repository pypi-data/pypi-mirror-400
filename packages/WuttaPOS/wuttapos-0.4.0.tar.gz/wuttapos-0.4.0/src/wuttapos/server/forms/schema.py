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
Form schema types
"""

from wuttaweb.forms.schema import ObjectRef


class StoreRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.stores.Store` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.Store

    def sort_query(self, query):
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):
        store = obj
        return self.request.route_url("stores.view", uuid=store.uuid)


class TerminalRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.terminals.Terminal` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.Terminal

    def sort_query(self, query):
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):
        terminal = obj
        return self.request.route_url("terminals.view", uuid=terminal.uuid)


class DepartmentRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.departments.Department` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.Department

    def sort_query(self, query):
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):
        department = obj
        return self.request.route_url("departments.view", uuid=department.uuid)


class EmployeeRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.employees.Employee` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.Employee

    def sort_query(self, query):
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):
        employee = obj
        return self.request.route_url("employees.view", uuid=employee.uuid)


class CustomerRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.customers.Customer` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.Customer

    def sort_query(self, query):
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):
        customer = obj
        return self.request.route_url("customers.view", uuid=customer.uuid)


class ProductRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.products.Product` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.Product

    def sort_query(self, query):
        return query.order_by(self.model_class.description)

    def get_object_url(self, obj):
        product = obj
        return self.request.route_url("products.view", uuid=product.uuid)


class InventoryAdjustmentTypeRef(ObjectRef):
    """
    Schema type for a
    :class:`~wuttapos.db.model.products.InventoryAdjustmentType`
    reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        model = self.app.model
        return model.InventoryAdjustmentType

    def sort_query(self, query):
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):
        adjustment_type = obj
        return self.request.route_url(
            "inventory_adjustment_types.view", uuid=adjustment_type.uuid
        )
