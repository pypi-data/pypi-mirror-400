# -*- coding: utf-8; -*-
"""
Model definition for Customers
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Customer(model.Base):
    """
    Technically a customer account, but relates to a person (account holder).
    """

    __tablename__ = "customer"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Customer",
        "model_title_plural": "Customers",
    }

    uuid = model.uuid_column()

    customer_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for the customer account.
        """,
    )

    name = sa.Column(
        sa.String(length=100),
        nullable=False,
        doc="""
        Name for the customer account.
        """,
    )

    account_holder_uuid = model.uuid_fk_column("person.uuid", nullable=True)
    account_holder = orm.relationship(
        "Person",
        doc="""
        Reference to the account holder, if applicable.
        """,
    )

    phone_number = sa.Column(
        sa.String(length=20),
        nullable=True,
        doc="""
        Phone number for the customer.
        """,
    )

    email_address = sa.Column(
        sa.String(length=255),
        nullable=True,
        doc="""
        Email address for the customer.
        """,
    )

    def __str__(self):
        return self.name or ""
