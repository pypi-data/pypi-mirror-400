# -*- coding: utf-8; -*-
"""
Model definition for Employees
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Employee(model.Base):
    """
    Represents a current or former employee.
    """

    __tablename__ = "employee"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Employee",
        "model_title_plural": "Employees",
    }

    uuid = model.uuid_column()

    person_uuid = model.uuid_fk_column("person.uuid", nullable=True)
    person = orm.relationship(
        "Person",
        doc="""
        Reference to the person who is/was the employee.
        """,
        backref=orm.backref(
            "employee",
            uselist=False,
            doc="""
            Reference to the employee record for the person, if applicable.
            """,
        ),
    )

    name = sa.Column(
        sa.String(length=100),
        nullable=False,
        doc="""
        Internal name for the employee.
        """,
    )

    public_name = sa.Column(
        sa.String(length=100),
        nullable=True,
        doc="""
        Name of the employee, for display to the public (if different).
        """,
    )

    active = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        doc="""
        Indicates the employee is currently active.
        """,
    )

    def __str__(self):
        return self.name or ""
