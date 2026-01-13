# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaPOS -- Point of Sale system based on Wutta Framework
#  Copyright © 2026 Lance Edgar
#
#  This file is part of WuttaPOS.
#
#  WuttaPOS is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  WuttaPOS is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  WuttaPOS.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Model for POS Batches
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from wuttjamaican.db import model


class POSBatch(model.BatchMixin, model.Base):
    """
    Hopefully generic batch used for entering new purchases into the system, etc.?
    """

    __tablename__ = "batch_pos"
    __wutta_hint__ = {
        "model_title": "POS Batch",
        "model_title_plural": "POS Batches",
    }

    batch_type = "pos"

    STATUS_OK = 1
    STATUS_SUSPENDED = 2

    STATUS = {
        STATUS_OK: "ok",
        STATUS_SUSPENDED: "suspended",
    }

    store_uuid = model.uuid_fk_column("store.uuid", nullable=False)
    store = orm.relationship(
        "Store",
        doc="""
        Reference to the store where the transaction ocurred.
        """,
    )

    terminal_uuid = model.uuid_fk_column("terminal.uuid", nullable=False)
    terminal = orm.relationship(
        "Terminal",
        doc="""
        Reference to the terminal where the transaction ocurred.
        """,
    )

    # receipt_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Receipt number for the transaction, if known.
    # """)

    cashier_uuid = model.uuid_fk_column("employee.uuid", nullable=False)
    cashier = orm.relationship(
        "Employee",
        doc="""
        Reference to the employee who acted as cashier.
        """,
    )

    customer_uuid = model.uuid_fk_column("customer.uuid", nullable=True)
    customer = orm.relationship(
        "Customer",
        doc="""
        Reference to the customer account for the transaction.
        """,
    )

    customer_is_member = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
    Flag indicating the customer was a "member" at time of sale.
    """,
    )

    customer_is_employee = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
    Flag indicating the customer was an employee at time of sale.
    """,
    )

    # shopper_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Number of the shopper account for the transaction, if applicable.
    # """)

    # shopper_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the shopper account for the transaction, if applicable.
    # """)

    # shopper_uuid = sa.Column(sa.String(length=32), nullable=True)
    # shopper = orm.relationship(
    #     'CustomerShopper',
    #     doc="""
    #     Reference to the shopper account for the transaction.
    #     """)

    sales_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Sales total for the transaction.
    """,
    )

    fs_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Portion of the sales total which is foodstamp-eligible.
    """,
    )

    tax_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Tax total for the transaction.
    """,
    )

    fs_tender_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Foodstamp tender total for the transaction.
    """,
    )

    tender_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Tender total for the transaction.
    """,
    )

    void = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        doc="""
    Flag indicating if the transaction was voided.
    """,
    )

    training_mode = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        doc="""
    Flag indicating if the transaction was rang in training mode,
    i.e. not real / should not go on the books.
    """,
    )

    def get_balance(self):
        return (
            (self.sales_total or 0) + (self.tax_total or 0) + (self.tender_total or 0)
        )

    def get_fs_balance(self):
        return (self.fs_total or 0) + (self.fs_tender_total or 0)


class POSBatchRow(model.BatchRowMixin, model.Base):
    """
    Row of data within a POS batch.
    """

    __tablename__ = "batch_pos_row"
    __batch_class__ = POSBatch

    STATUS_OK = 1

    STATUS = {
        STATUS_OK: "ok",
    }

    modified_by_uuid = model.uuid_fk_column("user.uuid", nullable=False)
    modified_by = orm.relationship(
        "User",
        doc="""
        Reference to the user who added this row to the batch.
        """,
    )

    row_type = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
    Type of item represented by this row, e.g. "item" or "return" or
    "tender" etc.

    .. todo::
       need to figure out how to manage/track POSBatchRow.row_type
    """,
    )

    item_entry = sa.Column(
        sa.String(length=20),
        nullable=True,
        doc="""
    Raw/original entry value for the item, if applicable.
    """,
    )

    description = sa.Column(
        sa.String(length=100),
        nullable=True,
        doc="""
    Description for the row.
    """,
    )

    product_uuid = model.uuid_fk_column("product.uuid", nullable=True)
    product = orm.relationship(
        "Product",
        doc="""
        Reference to the associated product, if applicable.
        """,
    )

    # department_uuid = model.uuid_fk_column("department.uuid", nullable=True)
    # department = orm.relationship(
    #     "Department",
    #     doc="""
    #     Reference to the associated department, if applicable.
    #     """,
    # )

    # subdepartment_number = sa.Column(
    #     sa.Integer(),
    #     nullable=True,
    #     doc="""
    # Number of the subdepartment to which the product belongs.
    # """,
    # )

    # subdepartment_name = sa.Column(
    #     sa.String(length=30),
    #     nullable=True,
    #     doc="""
    # Name of the subdepartment to which the product belongs.
    # """,
    # )

    foodstamp_eligible = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
    Indicates the item is eligible for purchase with food stamps
    or equivalent.
    """,
    )

    sold_by_weight = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
    Flag indicating the item is sold by weight.
    """,
    )

    quantity = sa.Column(
        sa.Numeric(precision=8, scale=2),
        nullable=True,
        doc="""
    Quantity for the item.
    """,
    )

    cost = sa.Column(
        sa.Numeric(precision=8, scale=3),
        nullable=True,
        doc="""
    Internal cost for the item sold.

    NOTE: this may need to change at some point, hence the "generic"
    naming so far.  would we need to record multiple kinds of costs?
    """,
    )

    reg_price = sa.Column(
        sa.Numeric(precision=8, scale=3),
        nullable=True,
        doc="""
    Regular price for the item.
    """,
    )

    cur_price = sa.Column(
        sa.Numeric(precision=8, scale=3),
        nullable=True,
        doc="""
    Current price for the item.
    """,
    )

    cur_price_type = sa.Column(
        sa.Integer(),
        nullable=True,
        doc="""
    Type code for the current price, if applicable.
    """,
    )

    cur_price_start = sa.Column(
        sa.DateTime(),
        nullable=True,
        doc="""
    Start date for current price, if applicable.
    """,
    )

    cur_price_end = sa.Column(
        sa.DateTime(),
        nullable=True,
        doc="""
    End date for current price, if applicable.
    """,
    )

    txn_price = sa.Column(
        sa.Numeric(precision=8, scale=3),
        nullable=True,
        doc="""
    Actual price paid for the item.
    """,
    )

    txn_price_adjusted = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
    Flag indicating the actual price was manually adjusted.
    """,
    )

    sales_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Sales total for the item.
    """,
    )

    tax_code = sa.Column(
        sa.String(length=30),
        nullable=True,
        doc="""
    Unique "code" for the item tax rate, if applicable.
    """,
    )

    # tax_uuid = model.uuid_fk_column("tax.uuid", nullable=True)
    # tax = orm.relationship(
    #     "Tax",
    #     doc="""
    #     Reference to the associated tax, if applicable.
    #     """,
    # )

    tender_total = sa.Column(
        sa.Numeric(precision=9, scale=2),
        nullable=True,
        doc="""
    Tender total for the item.
    """,
    )

    # tender_uuid = model.uuid_fk_column("tender.uuid", nullable=True)
    # tender = orm.relationship(
    #     "Tender",
    #     doc="""
    #     Reference to the associated tender, if applicable.
    #     """,
    # )

    void = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        doc="""
    Flag indicating the line item was voided.
    """,
    )
