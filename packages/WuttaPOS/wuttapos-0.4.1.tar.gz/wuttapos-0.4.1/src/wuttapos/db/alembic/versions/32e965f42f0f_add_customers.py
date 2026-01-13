"""add Customers

Revision ID: 32e965f42f0f
Revises: 6f02663c2220
Create Date: 2026-01-01 19:51:21.769137

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "32e965f42f0f"
down_revision: Union[str, None] = "6f02663c2220"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # customer
    op.create_table(
        "customer",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("customer_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("account_holder_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("email_address", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_holder_uuid"],
            ["person.uuid"],
            name=op.f("fk_customer_account_holder_uuid_person"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_customer")),
    )
    op.create_table(
        "customer_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "customer_id", sa.String(length=20), autoincrement=False, nullable=True
        ),
        sa.Column("name", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column(
            "account_holder_uuid",
            wuttjamaican.db.util.UUID(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "phone_number", sa.String(length=20), autoincrement=False, nullable=True
        ),
        sa.Column(
            "email_address", sa.String(length=255), autoincrement=False, nullable=True
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_customer_version")
        ),
    )
    op.create_index(
        op.f("ix_customer_version_end_transaction_id"),
        "customer_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_version_operation_type"),
        "customer_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_version_transaction_id"),
        "customer_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # customer
    op.drop_index(
        op.f("ix_customer_version_transaction_id"), table_name="customer_version"
    )
    op.drop_index(
        op.f("ix_customer_version_operation_type"), table_name="customer_version"
    )
    op.drop_index(
        op.f("ix_customer_version_end_transaction_id"), table_name="customer_version"
    )
    op.drop_table("customer_version")
    op.drop_table("customer")
