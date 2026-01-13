# -*- coding: utf-8; -*-
"""
Model definition for Products
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model
from wuttjamaican.db.util import UUID


class Product(model.Base):
    """
    Represents an item for sale (usually).
    """

    __tablename__ = "product"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Product",
        "model_title_plural": "Products",
    }

    uuid = model.uuid_column()

    product_id = sa.Column(
        sa.String(length=20),
        nullable=False,
        doc="""
        Unique identifier for the product.
        """,
    )

    brand_name = sa.Column(
        sa.String(length=100),
        nullable=True,
        doc="""
        Brand name for the product, if applicable.
        """,
    )

    description = sa.Column(
        sa.String(length=255),
        nullable=False,
        doc="""
        Description of the product.
        """,
    )

    size = sa.Column(
        sa.String(length=30),
        nullable=True,
        doc="""
        Size of the product.
        """,
    )

    sold_by_weight = sa.Column(
        sa.Boolean(),
        nullable=False,
        doc="""
        Indicates the item is sold by weight, vs. by single units.
        """,
    )

    department_uuid = model.uuid_fk_column("department.uuid", nullable=False)
    department = orm.relationship(
        "Department",
        doc="""
        Department to which the product belongs.
        """,
    )

    special_order = sa.Column(
        sa.Boolean(),
        nullable=True,
        doc="""
        Indicates the item is not normally carried, must be ordered specially.
        """,
    )

    case_size = sa.Column(
        sa.Numeric(precision=9, scale=4),
        nullable=True,
        doc="""
        Number of units in a case for this item, if applicable.
        """,
    )

    unit_cost = sa.Column(
        sa.Numeric(precision=9, scale=5),
        nullable=True,
        doc="""
        Current cost (from the vendor, to the retailer) for one unit of the item.
        """,
    )

    unit_price_reg = sa.Column(
        sa.Numeric(precision=8, scale=3),
        nullable=True,
        doc="""
        Regular price (to the customer) for one unit of product.
        """,
    )

    notes = sa.Column(
        sa.Text(),
        nullable=True,
        doc="""
        Arbitrary notes for the product.
        """,
    )

    inventory = orm.relationship(
        "ProductInventory",
        doc="""
        Reference to the live inventory record for this product.
        """,
        uselist=False,
        back_populates="product",
        cascade="all, delete-orphan",
    )

    @property
    def full_description(self):
        fields = [self.brand_name or "", self.description or "", self.size or ""]
        fields = [f.strip() for f in fields if f.strip()]
        return " ".join(fields)

    def __str__(self):
        return self.full_description


class ProductInventory(model.Base):
    """
    Contains the live inventory counts for products.
    """

    __tablename__ = "product_inventory"
    __wutta_hint__ = {
        "model_title": "Product Inventory",
        "model_title_plural": "Product Inventory",
    }

    uuid = model.uuid_column()

    product_uuid = model.uuid_fk_column("product.uuid", nullable=False)
    product = orm.relationship(
        "Product",
        doc="""
        Reference to the product.
        """,
        back_populates="inventory",
    )

    on_hand = sa.Column(
        sa.Numeric(precision=9, scale=4),
        nullable=True,
        doc="""
        Unit quantity of product which is currently on hand.
        """,
    )

    on_order = sa.Column(
        sa.Numeric(precision=9, scale=4),
        nullable=True,
        doc="""
        Unit quantity of product which is currently on order.
        """,
    )

    adjustments = orm.relationship(
        "InventoryAdjustment",
        back_populates="inventory",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return str(self.product or "")


class InventoryAdjustmentType(model.Base):
    """
    Possible types of inventory adjustments.
    """

    __tablename__ = "inventory_adjustment_type"
    __versioned__ = {}
    __wutta_hint__ = {
        "model_title": "Inventory Adjustment Type",
        "model_title_plural": "Inventory Adjustment Types",
    }

    uuid = model.uuid_column()

    type_code = sa.Column(
        sa.Integer(),
        nullable=False,
        unique=True,
        doc="""
        Code indicating the type of inventory adjustment.
        """,
    )

    name = sa.Column(
        sa.String(length=100),
        nullable=False,
        doc="""
        Name for the adjustment type.
        """,
    )

    def __str__(self):
        return self.name or ""


class InventoryAdjustment(model.Base):
    """
    Represents any adjustment to inventory.
    """

    __tablename__ = "inventory_adjustment"
    __wutta_hint__ = {
        "model_title": "Inventory Adjustment",
        "model_title_plural": "Inventory Adjustments",
    }

    uuid = model.uuid_column()

    inventory_uuid = model.uuid_fk_column("product_inventory.uuid", nullable=True)
    inventory = orm.relationship(
        "ProductInventory",
        doc="""
        Reference to the product inventory record.
        """,
        back_populates="adjustments",
    )

    adjusted = sa.Column(
        sa.DateTime(),
        nullable=False,
        doc="""
        Date and time (in UTC) when the adjustment occurred.
        """,
    )

    effective_date = sa.Column(
        sa.Date(),
        nullable=False,
        doc="""
        Effective date (in local time zone) for the adjustment.
        """,
    )

    adjustment_type_uuid = model.uuid_fk_column(
        "inventory_adjustment_type.uuid", nullable=True
    )
    adjustment_type = orm.relationship(
        "InventoryAdjustmentType",
        doc="""
        Reference to the adjustment type record.
        """,
    )

    amount = sa.Column(
        sa.Numeric(precision=9, scale=4),
        nullable=False,
        doc="""
        Amount of the adjustment; may be positive or negative.
        """,
    )

    source = sa.Column(
        sa.String(length=100),
        nullable=True,
        doc="""
        Arbitrary string identifying the source of the adjustment, if applicable.
        """,
    )

    def __str__(self):
        return str(self.inventory or "")
