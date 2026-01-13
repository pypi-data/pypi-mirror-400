# -*- coding: utf-8; -*-
"""
Master view for Employees
"""

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import PersonRef

from wuttapos.db.model import Employee


class EmployeeView(MasterView):
    """
    Master view for Employees
    """

    model_class = Employee
    model_title = "Employee"
    model_title_plural = "Employees"

    route_prefix = "employees"
    url_prefix = "/employees"

    creatable = True
    editable = True
    deletable = True

    grid_columns = [
        "person",
        "name",
        "public_name",
        "active",
    ]

    form_fields = [
        "person",
        "name",
        "public_name",
        "active",
    ]

    def configure_form(self, form):
        f = form
        super().configure_form(f)

        # person
        f.set_node("person", PersonRef(self.request))


def defaults(config, **kwargs):
    base = globals()

    EmployeeView = kwargs.get("EmployeeView", base["EmployeeView"])
    EmployeeView.defaults(config)


def includeme(config):
    defaults(config)
