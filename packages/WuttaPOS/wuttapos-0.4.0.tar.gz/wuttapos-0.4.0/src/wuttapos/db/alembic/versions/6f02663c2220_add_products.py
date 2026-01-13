"""add Products

Revision ID: 6f02663c2220
Revises: 148d701e4ac7
Create Date: 2026-01-01 18:18:22.958598

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "6f02663c2220"
down_revision: Union[str, None] = "148d701e4ac7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # product
    op.create_table(
        "product",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("product_id", sa.String(length=20), nullable=False),
        sa.Column("brand_name", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("size", sa.String(length=30), nullable=True),
        sa.Column("sold_by_weight", sa.Boolean(), nullable=False),
        sa.Column("department_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("special_order", sa.Boolean(), nullable=True),
        sa.Column("case_size", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("unit_cost", sa.Numeric(precision=9, scale=5), nullable=True),
        sa.Column("unit_price_reg", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_uuid"],
            ["department.uuid"],
            name=op.f("fk_product_department_uuid_department"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_product")),
    )
    op.create_table(
        "product_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "product_id", sa.String(length=20), autoincrement=False, nullable=True
        ),
        sa.Column(
            "brand_name", sa.String(length=100), autoincrement=False, nullable=True
        ),
        sa.Column(
            "description", sa.String(length=255), autoincrement=False, nullable=True
        ),
        sa.Column("size", sa.String(length=30), autoincrement=False, nullable=True),
        sa.Column("sold_by_weight", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            "department_uuid",
            wuttjamaican.db.util.UUID(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("special_order", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column(
            "case_size",
            sa.Numeric(precision=9, scale=4),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "unit_cost",
            sa.Numeric(precision=9, scale=5),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "unit_price_reg",
            sa.Numeric(precision=8, scale=3),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), autoincrement=False, nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_product_version")
        ),
    )
    op.create_index(
        op.f("ix_product_version_end_transaction_id"),
        "product_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_product_version_operation_type"),
        "product_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_product_version_transaction_id"),
        "product_version",
        ["transaction_id"],
        unique=False,
    )

    # product_inventory
    op.create_table(
        "product_inventory",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("product_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("on_hand", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.Column("on_order", sa.Numeric(precision=9, scale=4), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_uuid"],
            ["product.uuid"],
            name=op.f("fk_product_inventory_product_uuid_product"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_product_inventory")),
    )

    # inventory_adjustment_type
    op.create_table(
        "inventory_adjustment_type",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("type_code", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_inventory_adjustment_type")),
        sa.UniqueConstraint(
            "type_code", name=op.f("uq_inventory_adjustment_type_type_code")
        ),
    )
    op.create_table(
        "inventory_adjustment_type_version",
        sa.Column(
            "uuid", wuttjamaican.db.util.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("type_code", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column("name", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "uuid", "transaction_id", name=op.f("pk_inventory_adjustment_type_version")
        ),
    )
    op.create_index(
        op.f("ix_inventory_adjustment_type_version_end_transaction_id"),
        "inventory_adjustment_type_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_adjustment_type_version_operation_type"),
        "inventory_adjustment_type_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_adjustment_type_version_transaction_id"),
        "inventory_adjustment_type_version",
        ["transaction_id"],
        unique=False,
    )

    # inventory_adjustment
    op.create_table(
        "inventory_adjustment",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("inventory_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("adjusted", sa.DateTime(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("adjustment_type_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["adjustment_type_uuid"],
            ["inventory_adjustment_type.uuid"],
            name=op.f(
                "fk_inventory_adjustment_adjustment_type_uuid_inventory_adjustment_type"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["inventory_uuid"],
            ["product_inventory.uuid"],
            name=op.f("fk_inventory_adjustment_inventory_uuid_product_inventory"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_inventory_adjustment")),
    )


def downgrade() -> None:

    # inventory_adjustment
    op.drop_table("inventory_adjustment")

    # inventory_adjustment_type
    op.drop_index(
        op.f("ix_inventory_adjustment_type_version_transaction_id"),
        table_name="inventory_adjustment_type_version",
    )
    op.drop_index(
        op.f("ix_inventory_adjustment_type_version_operation_type"),
        table_name="inventory_adjustment_type_version",
    )
    op.drop_index(
        op.f("ix_inventory_adjustment_type_version_end_transaction_id"),
        table_name="inventory_adjustment_type_version",
    )
    op.drop_table("inventory_adjustment_type_version")
    op.drop_table("inventory_adjustment_type")

    # product_inventory
    op.drop_table("product_inventory")

    # product
    op.drop_index(
        op.f("ix_product_version_transaction_id"), table_name="product_version"
    )
    op.drop_index(
        op.f("ix_product_version_operation_type"), table_name="product_version"
    )
    op.drop_index(
        op.f("ix_product_version_end_transaction_id"), table_name="product_version"
    )
    op.drop_table("product_version")
    op.drop_table("product")
