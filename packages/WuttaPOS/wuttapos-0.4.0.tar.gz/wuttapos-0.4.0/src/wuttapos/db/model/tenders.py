# -*- coding: utf-8; -*-
"""
Model definition for Tenders
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Tender(model.Base):
    """
    Represents a tender (payment type) for the POS.
    """

    __tablename__ = "tender"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Tender",
        "model_title_plural": "Tenders",
    }

    uuid = model.uuid_column()

    tender_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for the tender.
        """,
    )

    name = sa.Column(
        sa.String(length=50),
        nullable=False,
        doc="""
        Name for the tender type.
        """,
    )

    notes = sa.Column(
        sa.Text(),
        nullable=True,
        doc="""
        Arbitrary notes for the tender type.
        """,
    )

    is_cash = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates this tender type is a form of "cash" conceptually.
        """,
    )

    is_foodstamp = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates this tender type is a form of "food stamps" conceptually.
        """,
    )

    allow_cashback = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates "cash back" should be allowed when overpaying with this tender.
        """,
    )

    kick_drawer = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates the cash drawer should kick open when accepting this tender.
        """,
    )

    active = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        doc="""
        Indicates this tender is currently active (acceptable for payment).
        """,
    )

    def __str__(self):
        return self.name or ""
