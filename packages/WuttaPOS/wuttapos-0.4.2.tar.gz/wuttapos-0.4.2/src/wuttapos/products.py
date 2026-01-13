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
Products Handler
"""

# import decimal
import logging
import uuid as _uuid

from sqlalchemy import orm

from wuttjamaican.app import GenericHandler


log = logging.getLogger(__name__)


class ProductsHandler(GenericHandler):
    """
    Base class and default implementation for product handlers.

    A products handler of course should get the final say in how products are
    handled.  This means everything from pricing, to whether or not a
    particular product can be deleted, etc.
    """

    def locate_product_for_entry(
        self, session, entry, include_not_for_sale=False, **kwargs
    ):
        """
        This method aims to provide sane default logic for locating a
        :class:`~rattail.db.model.products.Product` record for the
        given "entry" value.

        The default logic here will try to honor the "configured"
        product key field, and prefer that when attempting the lookup.

        :param session: Reference to current DB session.

        :param entry: Value to use for lookup.  This is most often a
           simple string, but the method can handle a few others.  For
           instance it is common to read values from a spreadsheet,
           and sometimes those come through as integers etc.  If this
           value is a :class:`~rattail.gpc.GPC` instance, special
           logic may be used for the lookup.

        :param lookup_fields: Optional list of fields to use for
           lookup.  The default value is ``['uuid', '_product_key_']``
           which means to lookup by UUID as well as "product key"
           field, which is configurable.  You can include any of the
           following in ``lookup_fields``:

           * ``uuid``
           * ``_product_key_`` - :meth:`locate_product_for_key`
           * ``upc`` - :meth:`locate_product_for_upc`
           * ``item_id`` - :meth:`locate_product_for_item_id`
           * ``scancode`` - :meth:`locate_product_for_scancode`
           * ``vendor_code`` - :meth:`locate_product_for_vendor_code`
           * ``alt_code`` - :meth:`locate_product_for_alt_code`

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        model = self.app.model
        if not entry:
            return

        # figure out which fields we should match on
        # TODO: let config declare default lookup_fields
        lookup_fields = kwargs.pop(
            "lookup_fields",
            [
                "uuid",
                "product_id",
            ],
        )

        kwargs["include_not_for_sale"] = include_not_for_sale

        # try to locate product by uuid before other, more specific key
        if "uuid" in lookup_fields:
            if isinstance(entry, (_uuid.UUID, str)):
                if product := session.get(model.Product, entry):
                    return product
                # # TODO: should we ever return deleted product?
                # if product and not product.deleted:
                #     if include_not_for_sale or not product.not_for_sale:
                #         return product

        lookups = {
            "uuid": None,
            "product_id": self.locate_product_for_id,
            # "upc": self.locate_product_for_upc,
            # "item_id": self.locate_product_for_item_id,
            # "scancode": self.locate_product_for_scancode,
            # "vendor_code": self.locate_product_for_vendor_code,
            # "alt_code": self.locate_product_for_alt_code,
        }

        for field in lookup_fields:
            if field in lookups:
                lookup = lookups[field]
                if lookup:
                    product = lookup(session, entry, **kwargs)
                    if product:
                        return product
            else:
                log.warning("unknown lookup field: %s", field)

    def locate_product_for_id(
        self,
        session,
        entry,
        # include_not_for_sale=False,
        # include_deleted=False,
        **kwargs,
    ):
        """
        Locate the product which matches the given item ID.

        This will do a lookup on the
        :attr:`rattail.db.model.products.Product.item_id` field only.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_product_for_key` instead.

        :param session: Current session for Rattail DB.

        :param entry: Item ID value as string.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :param include_deleted: Whether "deleted" products should ever
           match (and be returned).

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        if not entry:
            return

        # assume entry is string
        entry = str(entry)

        model = self.app.model
        products = session.query(model.Product)
        # if not include_deleted:
        #     products = products.filter(model.Product.deleted == False)
        # if not include_not_for_sale:
        #     products = products.filter(model.Product.not_for_sale == False)

        try:
            return products.filter(model.Product.product_id == entry).one()
        except orm.exc.NoResultFound:
            return None

    def search_products(self, session, entry, **kwargs):
        """
        Perform a product search across multiple fields, and return
        results as JSON data rows.
        """
        model = self.app.model
        final_results = []

        # first we'll attempt "lookup" logic..

        lookup_fields = kwargs.get(
            "lookup_fields",
            [
                # "_product_key_",
                "product_id"
            ],
        )

        if lookup_fields:
            product = self.locate_product_for_entry(
                session, entry, lookup_fields=lookup_fields
            )
            if product:
                final_results.append(product)

        # then we'll attempt "search" logic..

        search_fields = kwargs.get(
            "search_fields",
            [
                "product_id",
                "brand",
                "description",
                "size",
            ],
        )

        searches = {
            "product_id": self.search_products_for_product_id,
            "brand": self.search_products_for_brand,
            "description": self.search_products_for_description,
            "size": self.search_products_for_size,
        }

        for field in search_fields:
            if field in searches:
                search = searches[field]
                if search:
                    products = search(session, entry, **kwargs)
                    final_results.extend(products)
            else:
                log.warning("unknown search field: %s", field)

        return [self.normalize_product(c) for c in final_results]

    def search_products_for_product_id(
        self,
        session,
        entry,
        # include_not_for_sale=False,
    ):
        """
        Search for products where the
        :attr:`~rattail.db.model.products.Product.item_id` contains
        the given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.app.model
        entry = entry.lower()

        products = session.query(model.Product).filter(
            model.Product.product_id.ilike(f"%{entry}%")
        )

        # if not include_not_for_sale:
        #     products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def search_products_for_brand(
        self,
        session,
        entry,
        # include_not_for_sale=False,
    ):
        """
        Search for products where the brand
        :attr:`~rattail.db.model.products.Brand.name` contains the
        given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.app.model
        entry = entry.lower()

        products = session.query(model.Product).filter(
            model.Product.brand_name.ilike(f"%{entry}%")
        )

        # if not include_not_for_sale:
        #     products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def search_products_for_description(
        self,
        session,
        entry,
        # include_not_for_sale=False,
    ):
        """
        Search for products where the
        :attr:`~rattail.db.model.products.Product.description`
        contains the given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.app.model
        entry = entry.lower()

        products = session.query(model.Product).filter(
            model.Product.description.ilike(f"%{entry}%")
        )

        # if not include_not_for_sale:
        #     products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def search_products_for_size(
        self,
        session,
        entry,
        # include_not_for_sale=False,
    ):
        """
        Search for products where the
        :attr:`~rattail.db.model.products.Product.size` contains the
        given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.app.model
        entry = entry.lower()

        products = session.query(model.Product).filter(
            model.Product.size.ilike(f"%{entry}%")
        )

        # if not include_not_for_sale:
        #     products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def normalize_product(self, product, fields=None):
        """
        Normalize the given product to a JSON-serializable dict.
        """
        data = {
            "uuid": product.uuid,
            "product_id": product.product_id,
            "description": product.description,
            "size": product.size,
            "_str": str(product),
        }

        if not fields:
            fields = [
                "brand_name",
                "full_description",
                "department_name",
                "unit_price_display",
            ]

        if "brand_name" in fields:
            data["brand_name"] = product.brand_name

        if "full_description" in fields:
            data["full_description"] = product.full_description

        if "department_name" in fields:
            data["department_name"] = (
                product.department.name if product.department else None
            )

        if "unit_price_display" in fields:
            data["unit_price_display"] = self.app.render_currency(
                product.unit_price_reg
            )

        # if "vendor_name" in fields:
        #     vendor = product.cost.vendor if product.cost else None
        #     data["vendor_name"] = vendor.name if vendor else None

        # if "costs" in fields:
        #     costs = []
        #     for cost in product.costs:
        #         costs.append(
        #             {
        #                 "uuid": cost.uuid,
        #                 "vendor_uuid": cost.vendor_uuid,
        #                 "vendor_name": cost.vendor.name,
        #                 "preference": cost.preference,
        #                 "code": cost.code,
        #                 "case_size": cost.case_size,
        #                 "case_cost": cost.case_cost,
        #                 "unit_cost": cost.unit_cost,
        #             }
        #         )
        #     data["costs"] = costs

        # current_price = None
        # if not product.not_for_sale:

        #     margin_fields = [
        #         "true_margin",
        #         "true_margin_display",
        #     ]
        #     if any([f in fields for f in margin_fields]):
        #         if product.volatile:
        #             data["true_margin"] = product.volatile.true_margin
        #             data["true_margin_display"] = self.app.render_percent(
        #                 product.volatile.true_margin, places=2
        #             )

        #     current_fields = [
        #         "current_price",
        #         "current_price_display",
        #         "current_ends",
        #         "current_ends_display",
        #     ]
        #     if any([f in fields for f in current_fields]):
        #         current_price = product.current_price
        #         if current_price:
        #             if current_price.price:
        #                 data["current_price"] = float(current_price.price)
        #             data["current_price_display"] = self.render_price(current_price)
        #             current_ends = current_price.ends
        #             if current_ends:
        #                 current_ends = self.app.localtime(
        #                     current_ends, from_utc=True
        #                 ).date()
        #                 data["current_ends"] = str(current_ends)
        #                 data["current_ends_display"] = self.app.render_date(
        #                     current_ends
        #                 )

        #     sale_fields = [
        #         "sale_price",
        #         "sale_price_display",
        #         "sale_ends",
        #         "sale_ends_display",
        #     ]
        #     if any([f in fields for f in sale_fields]):
        #         sale_price = product.sale_price
        #         if sale_price:
        #             if sale_price.price:
        #                 data["sale_price"] = float(sale_price.price)
        #             data["sale_price_display"] = self.render_price(sale_price)
        #             sale_ends = sale_price.ends
        #             if sale_ends:
        #                 sale_ends = self.app.localtime(sale_ends, from_utc=True).date()
        #                 data["sale_ends"] = str(sale_ends)
        #                 data["sale_ends_display"] = self.app.render_date(sale_ends)

        #     tpr_fields = [
        #         "tpr_price",
        #         "tpr_price_display",
        #         "tpr_ends",
        #         "tpr_ends_display",
        #     ]
        #     if any([f in fields for f in tpr_fields]):
        #         tpr_price = product.tpr_price
        #         if tpr_price:
        #             if tpr_price.price:
        #                 data["tpr_price"] = float(tpr_price.price)
        #             data["tpr_price_display"] = self.render_price(tpr_price)
        #             tpr_ends = tpr_price.ends
        #             if tpr_ends:
        #                 tpr_ends = self.app.localtime(tpr_ends, from_utc=True).date()
        #                 data["tpr_ends"] = str(tpr_ends)
        #                 data["tpr_ends_display"] = self.app.render_date(tpr_ends)

        if "case_size" in fields:
            data["case_size"] = self.app.render_quantity(self.get_case_size(product))

        # if "case_price" in fields or "case_price_display" in fields:
        #     case_price = None
        #     if product.regular_price and product.regular_price is not None:
        #         case_size = self.get_case_size(product)
        #         # use "current" price if there is one, else normal unit price
        #         unit_price = product.regular_price.price
        #         if current_price:
        #             unit_price = current_price.price
        #         case_price = (case_size or 1) * unit_price
        #         case_price = case_price.quantize(decimal.Decimal("0.01"))
        #     data["case_price"] = str(case_price) if case_price is not None else None
        #     data["case_price_display"] = self.app.render_currency(case_price)

        # if "uom_choices" in fields:
        #     data["uom_choices"] = self.get_uom_choices(product)

        return data

    def get_case_size(self, product):
        """
        Return the effective case size for the given product.
        """
        if product.case_size is not None:
            return product.case_size

        # cost = product.cost
        # if cost:
        #     return cost.case_size

        return None
