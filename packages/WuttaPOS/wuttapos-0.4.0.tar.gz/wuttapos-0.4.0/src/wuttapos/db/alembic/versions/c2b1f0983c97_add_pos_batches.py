"""add POS Batches

Revision ID: c2b1f0983c97
Revises: 7067ef686eb0
Create Date: 2026-01-02 13:11:37.703157

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "c2b1f0983c97"
down_revision: Union[str, None] = "7067ef686eb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # batch_pos
    op.create_table(
        "batch_pos",
        sa.Column("store_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("terminal_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("cashier_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("customer_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("customer_is_member", sa.Boolean(), nullable=True),
        sa.Column("customer_is_employee", sa.Boolean(), nullable=True),
        sa.Column("sales_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("fs_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("tax_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("fs_tender_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("tender_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("void", sa.Boolean(), nullable=False),
        sa.Column("training_mode", sa.Boolean(), nullable=False),
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("status_text", sa.String(length=255), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("executed", sa.DateTime(), nullable=True),
        sa.Column("executed_by_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cashier_uuid"],
            ["employee.uuid"],
            name=op.f("fk_batch_pos_cashier_uuid_employee"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_uuid"],
            ["user.uuid"],
            name=op.f("fk_batch_pos_created_by_uuid_user"),
        ),
        sa.ForeignKeyConstraint(
            ["customer_uuid"],
            ["customer.uuid"],
            name=op.f("fk_batch_pos_customer_uuid_customer"),
        ),
        sa.ForeignKeyConstraint(
            ["executed_by_uuid"],
            ["user.uuid"],
            name=op.f("fk_batch_pos_executed_by_uuid_user"),
        ),
        sa.ForeignKeyConstraint(
            ["store_uuid"], ["store.uuid"], name=op.f("fk_batch_pos_store_uuid_store")
        ),
        sa.ForeignKeyConstraint(
            ["terminal_uuid"],
            ["terminal.uuid"],
            name=op.f("fk_batch_pos_terminal_uuid_terminal"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_batch_pos")),
    )

    # batch_pos_row
    op.create_table(
        "batch_pos_row",
        sa.Column("modified_by_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("row_type", sa.String(length=20), nullable=False),
        sa.Column("item_entry", sa.String(length=20), nullable=True),
        sa.Column("product_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.Column("foodstamp_eligible", sa.Boolean(), nullable=True),
        sa.Column("sold_by_weight", sa.Boolean(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("cost", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("reg_price", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("cur_price", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("cur_price_type", sa.Integer(), nullable=True),
        sa.Column("cur_price_start", sa.DateTime(), nullable=True),
        sa.Column("cur_price_end", sa.DateTime(), nullable=True),
        sa.Column("txn_price", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("txn_price_adjusted", sa.Boolean(), nullable=True),
        sa.Column("sales_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("tax_code", sa.String(length=30), nullable=True),
        sa.Column("tender_total", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("void", sa.Boolean(), nullable=False),
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("batch_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("status_text", sa.String(length=255), nullable=True),
        sa.Column("modified", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["batch_uuid"],
            ["batch_pos.uuid"],
            name=op.f("fk_batch_pos_row_batch_uuid_batch_pos"),
        ),
        sa.ForeignKeyConstraint(
            ["modified_by_uuid"],
            ["user.uuid"],
            name=op.f("fk_batch_pos_row_modified_by_uuid_user"),
        ),
        sa.ForeignKeyConstraint(
            ["product_uuid"],
            ["product.uuid"],
            name=op.f("fk_batch_pos_row_product_uuid_product"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_batch_pos_row")),
    )


def downgrade() -> None:

    # batch_pos*
    op.drop_table("batch_pos_row")
    op.drop_table("batch_pos")
