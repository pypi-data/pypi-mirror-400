# -*- coding: utf-8; -*-
"""
Model definition for Taxes
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Tax(model.Base):
    """
    Represents a type/rate of sales tax to track.
    """

    __tablename__ = "tax"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Tax",
        "model_title_plural": "Taxes",
    }

    uuid = model.uuid_column()

    tax_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for this tax rate.
        """,
    )

    name = sa.Column(
        sa.String(length=50),
        nullable=False,
        doc="""
        Name for the tax rate.
        """,
    )

    rate = sa.Column(
        sa.Numeric(precision=7, scale=5),
        nullable=False,
        doc="""
        Percentage rate for the tax, e.g. 8.25.
        """,
    )

    def __str__(self):
        return self.name or ""
