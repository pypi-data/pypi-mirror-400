# -*- coding: utf-8; -*-
"""
Model definition for Stores
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Store(model.Base):
    """
    Represents a single location, physical or virtual, where sales happen.
    """

    __tablename__ = "store"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Store",
        "model_title_plural": "Stores",
    }

    uuid = model.uuid_column()

    store_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for the store.
        """,
    )

    name = sa.Column(
        sa.String(length=100),
        nullable=False,
        doc="""
        Name for the store.
        """,
    )

    active = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        doc="""
        Indicates the store is currently active.
        """,
    )

    def __str__(self):
        return self.name or ""
