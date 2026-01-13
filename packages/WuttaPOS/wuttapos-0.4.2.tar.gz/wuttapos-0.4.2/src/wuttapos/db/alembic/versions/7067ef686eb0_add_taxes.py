"""add Taxes

Revision ID: 7067ef686eb0
Revises: b026e4f5c5bc
Create Date: 2026-01-02 12:15:45.279817

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "7067ef686eb0"
down_revision: Union[str, None] = "b026e4f5c5bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # tax
    op.create_table(
        "tax",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("tax_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("rate", sa.Numeric(precision=7, scale=5), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_tax")),
    )
    op.create_table(
        "tax_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("tax_id", sa.String(length=20), autoincrement=False, nullable=True),
        sa.Column("name", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column(
            "rate", sa.Numeric(precision=7, scale=5), autoincrement=False, nullable=True
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("uuid", "transaction_id", name=op.f("pk_tax_version")),
    )
    op.create_index(
        op.f("ix_tax_version_end_transaction_id"),
        "tax_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tax_version_operation_type"),
        "tax_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tax_version_transaction_id"),
        "tax_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # tax
    op.drop_table("batch_pos_row")
    op.drop_table("batch_pos")
    op.drop_index(op.f("ix_tax_version_transaction_id"), table_name="tax_version")
    op.drop_index(op.f("ix_tax_version_operation_type"), table_name="tax_version")
    op.drop_index(op.f("ix_tax_version_end_transaction_id"), table_name="tax_version")
    op.drop_table("tax_version")
    op.drop_table("tax")
