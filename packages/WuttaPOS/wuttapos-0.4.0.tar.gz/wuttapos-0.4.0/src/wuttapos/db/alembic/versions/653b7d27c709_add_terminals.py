"""add Terminals

Revision ID: 653b7d27c709
Revises: 3f548013be91
Create Date: 2026-01-02 11:08:43.118117

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "653b7d27c709"
down_revision: Union[str, None] = "3f548013be91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # terminal
    op.create_table(
        "terminal",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("terminal_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_terminal")),
    )
    op.create_table(
        "terminal_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "terminal_id", sa.String(length=20), autoincrement=False, nullable=True
        ),
        sa.Column("name", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_terminal_version")
        ),
    )
    op.create_index(
        op.f("ix_terminal_version_end_transaction_id"),
        "terminal_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_terminal_version_operation_type"),
        "terminal_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_terminal_version_transaction_id"),
        "terminal_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # terminal
    op.drop_index(
        op.f("ix_terminal_version_transaction_id"), table_name="terminal_version"
    )
    op.drop_index(
        op.f("ix_terminal_version_operation_type"), table_name="terminal_version"
    )
    op.drop_index(
        op.f("ix_terminal_version_end_transaction_id"), table_name="terminal_version"
    )
    op.drop_table("terminal_version")
    op.drop_table("terminal")
