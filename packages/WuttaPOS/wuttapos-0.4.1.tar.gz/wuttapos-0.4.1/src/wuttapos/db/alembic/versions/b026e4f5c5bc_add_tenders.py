"""add Tenders

Revision ID: b026e4f5c5bc
Revises: 8ce8b14af66d
Create Date: 2026-01-02 11:34:27.523125

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "b026e4f5c5bc"
down_revision: Union[str, None] = "8ce8b14af66d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # tender
    op.create_table(
        "tender",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("tender_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_cash", sa.Boolean(), nullable=False),
        sa.Column("is_foodstamp", sa.Boolean(), nullable=False),
        sa.Column("allow_cashback", sa.Boolean(), nullable=False),
        sa.Column("kick_drawer", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_tender")),
    )
    op.create_table(
        "tender_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "tender_id", sa.String(length=20), autoincrement=False, nullable=True
        ),
        sa.Column("name", sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column("notes", sa.Text(), autoincrement=False, nullable=True),
        sa.Column("is_cash", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("is_foodstamp", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("allow_cashback", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("kick_drawer", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("active", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_tender_version")
        ),
    )
    op.create_index(
        op.f("ix_tender_version_end_transaction_id"),
        "tender_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tender_version_operation_type"),
        "tender_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tender_version_transaction_id"),
        "tender_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # tender
    op.drop_index(op.f("ix_tender_version_transaction_id"), table_name="tender_version")
    op.drop_index(op.f("ix_tender_version_operation_type"), table_name="tender_version")
    op.drop_index(
        op.f("ix_tender_version_end_transaction_id"), table_name="tender_version"
    )
    op.drop_table("tender_version")
    op.drop_table("tender")
