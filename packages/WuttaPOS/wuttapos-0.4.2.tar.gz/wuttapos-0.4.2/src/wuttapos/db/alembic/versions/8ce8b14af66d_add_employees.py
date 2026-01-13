"""add Employees

Revision ID: 8ce8b14af66d
Revises: 653b7d27c709
Create Date: 2026-01-02 11:18:07.359270

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "8ce8b14af66d"
down_revision: Union[str, None] = "653b7d27c709"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # employee
    op.create_table(
        "employee",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("person_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("public_name", sa.String(length=100), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["person_uuid"],
            ["person.uuid"],
            name=op.f("fk_employee_person_uuid_person"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_employee")),
    )
    op.create_table(
        "employee_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "person_uuid",
            wuttjamaican.db.util.UUID(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("name", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column(
            "public_name", sa.String(length=100), autoincrement=False, nullable=True
        ),
        sa.Column("active", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_employee_version")
        ),
    )
    op.create_index(
        op.f("ix_employee_version_end_transaction_id"),
        "employee_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_employee_version_operation_type"),
        "employee_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_employee_version_transaction_id"),
        "employee_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:

    # employee
    op.drop_index(
        op.f("ix_employee_version_transaction_id"), table_name="employee_version"
    )
    op.drop_index(
        op.f("ix_employee_version_operation_type"), table_name="employee_version"
    )
    op.drop_index(
        op.f("ix_employee_version_end_transaction_id"), table_name="employee_version"
    )
    op.drop_table("employee_version")
    op.drop_table("employee")
