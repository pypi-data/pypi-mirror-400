"""add Departments

Revision ID: 148d701e4ac7
Revises:
Create Date: 2026-01-01 17:26:20.695393

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "148d701e4ac7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ("wuttapos",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # department
    op.create_table(
        "department",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("department_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("for_products", sa.Boolean(), nullable=False),
        sa.Column("for_personnel", sa.Boolean(), nullable=False),
        sa.Column("exempt_from_gross_sales", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_department")),
    )
    op.create_table(
        "department_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "department_id", sa.String(length=20), autoincrement=False, nullable=True
        ),
        sa.Column("name", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column("for_products", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("for_personnel", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            "exempt_from_gross_sales", sa.Boolean(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_department_version")
        ),
    )
    op.create_index(
        op.f("ix_department_version_end_transaction_id"),
        "department_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_department_version_operation_type"),
        "department_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_department_version_transaction_id"),
        "department_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # department
    op.drop_index(
        op.f("ix_department_version_transaction_id"), table_name="department_version"
    )
    op.drop_index(
        op.f("ix_department_version_operation_type"), table_name="department_version"
    )
    op.drop_index(
        op.f("ix_department_version_end_transaction_id"),
        table_name="department_version",
    )
    op.drop_table("department_version")
    op.drop_table("department")
