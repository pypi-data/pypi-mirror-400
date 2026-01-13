"""add Stores

Revision ID: 3f548013be91
Revises: 7880450562d5
Create Date: 2026-01-02 10:18:20.199691

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "3f548013be91"
down_revision: Union[str, None] = "32e965f42f0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # store
    op.create_table(
        "store",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("store_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_store")),
    )
    op.create_table(
        "store_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("store_id", sa.String(length=20), autoincrement=False, nullable=True),
        sa.Column("name", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column("active", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_store_version")
        ),
    )
    op.create_index(
        op.f("ix_store_version_end_transaction_id"),
        "store_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_store_version_operation_type"),
        "store_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_store_version_transaction_id"),
        "store_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # store
    op.drop_index(op.f("ix_store_version_transaction_id"), table_name="store_version")
    op.drop_index(op.f("ix_store_version_operation_type"), table_name="store_version")
    op.drop_index(
        op.f("ix_store_version_end_transaction_id"), table_name="store_version"
    )
    op.drop_table("store_version")
    op.drop_table("store")
