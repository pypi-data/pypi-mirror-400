# -*- coding: utf-8; -*-
"""
Model definition for Terminals
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model


class Terminal(model.Base):
    """
    Represents a POS terminal (lane).
    """

    __tablename__ = "terminal"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Terminal",
        "model_title_plural": "Terminals",
    }

    uuid = model.uuid_column()

    terminal_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for the terminal.
        """,
    )

    name = sa.Column(
        sa.String(length=50),
        nullable=False,
        doc="""
        Name for the terminal.
        """,
    )

    def __str__(self):
        return self.name or ""
