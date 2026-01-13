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
Clientele Handler
"""

# from collections import OrderedDict
import logging
import uuid as _uuid

# import warnings

from sqlalchemy import orm

from wuttjamaican.app import GenericHandler


log = logging.getLogger(__name__)


class ClienteleHandler(GenericHandler):
    """
    Base class and default implementation for clientele handlers.
    """

    # def get_customer(self, obj):
    #     """
    #     Return the Customer associated with the given object, if any.
    #     """
    #     model = self.model

    #     if isinstance(obj, model.Customer):
    #         return obj

    #     else:
    #         person = self.app.get_person(obj)
    #         if person:
    #             # TODO: all 3 options below are indeterminate, since it's
    #             # *possible* for a person to hold multiple accounts
    #             # etc. but not sure how to fix in a generic way?  maybe
    #             # just everyone must override as needed
    #             if person.customer_accounts:
    #                 return person.customer_accounts[0]
    #             for shopper in person.customer_shoppers:
    #                 if shopper.shopper_number == 1:
    #                     return shopper.customer
    #             # legacy fallback
    #             if person.customers:
    #                 return person.customers[0]

    # def make_customer(self, person, **kwargs):
    #     """
    #     Create and return a new customer record.
    #     """
    #     session = self.app.get_session(person)
    #     customer = self.model.Customer()
    #     customer.name = person.display_name
    #     customer.account_holder = person
    #     session.add(customer)
    #     session.flush()
    #     session.refresh(person)
    #     return customer

    def locate_customer_for_entry(self, session, entry, **kwargs):
        """
        This method aims to provide sane default logic for locating a
        :class:`~rattail.db.model.customers.Customer` record for the
        given "entry" value.

        The default logic here will try to honor the "configured"
        customer field, and prefer that when attempting the lookup.

        :param session: Reference to current DB session.

        :param entry: Value to use for lookup.  This is most often a
           simple string, but the method can handle a few others.  For
           instance it is common to read values from a spreadsheet,
           and sometimes those come through as integers etc.

        :param lookup_fields: Optional list of fields to use for
           lookup.  The default value is ``['uuid', '_customer_key_']``
           which means to lookup by UUID as well as "customer key"
           field, which is configurable.  You can include any of the
           following in ``lookup_fields``:

           * ``uuid``
           * ``_customer_key_`` - :meth:`locate_customer_for_key`

        :returns: First :class:`~rattail.db.model.customers.Customer`
           instance found if there was a match; otherwise ``None``.
        """
        model = self.app.model
        if not entry:
            return None

        # figure out which fields we should match on
        # TODO: let config declare default lookup_fields
        lookup_fields = kwargs.get(
            "lookup_fields",
            [
                "uuid",
                "customer_id",
            ],
        )

        # try to locate customer by uuid before other, more specific key
        if "uuid" in lookup_fields:
            if isinstance(entry, (_uuid.UUID, str)):
                customer = session.get(model.Customer, entry)
                if customer:
                    return customer

        lookups = {
            "uuid": None,
            "customer_id": self.locate_customer_for_id,
        }

        for field in lookup_fields:
            if field in lookups:
                lookup = lookups[field]
                if lookup:
                    customer = lookup(session, entry, **kwargs)
                    if customer:
                        return customer
            else:
                log.warning("unknown lookup field: %s", field)

    def locate_customer_for_id(self, session, entry, **kwargs):
        """
        Locate the customer which matches the given ID.

        This will do a lookup on the
        :attr:`rattail.db.model.customers.Customer.id` field only.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_customer_for_key()` instead.

        :param session: Current session for Rattail DB.

        :param entry: Customer ID value as string.

        :returns: First :class:`~rattail.db.model.customers.Customer`
           instance found if there was a match; otherwise ``None``.
        """
        if not entry:
            return None

        # assume entry is string
        entry = str(entry)

        model = self.app.model
        try:
            return (
                session.query(model.Customer)
                .filter(model.Customer.customer_id == entry)
                .one()
            )
        except orm.exc.NoResultFound:
            return None

    def search_customers(self, session, entry, **kwargs):
        """
        Perform a customer search across multiple fields, and return
        results as JSON data rows.
        """
        model = self.app.model
        final_results = []

        # first we'll attempt "lookup" logic..

        lookup_fields = kwargs.get(
            "lookup_fields",
            ["customer_id"],
        )

        if lookup_fields:
            customer = self.locate_customer_for_entry(
                session, entry, lookup_fields=lookup_fields
            )
            if customer:
                final_results.append(customer)

        # then we'll attempt "search" logic..

        search_fields = kwargs.get(
            "search_fields",
            [
                "name",
                "email_address",
                "phone_number",
            ],
        )

        searches = {
            "name": self.search_customers_for_name,
            "email_address": self.search_customers_for_email_address,
            "phone_number": self.search_customers_for_phone_number,
        }

        for field in search_fields:
            if field in searches:
                search = searches[field]
                if search:
                    customers = search(session, entry, **kwargs)
                    final_results.extend(customers)
            else:
                log.warning("unknown search field: %s", field)

        return [self.normalize_customer(c) for c in final_results]

    def search_customers_for_name(self, session, entry, **kwargs):
        model = self.app.model
        entry = entry.lower()

        return (
            session.query(model.Customer)
            .filter(model.Customer.name.ilike(f"%{entry}%"))
            .all()
        )

    def search_customers_for_email_address(self, session, entry, **kwargs):
        model = self.app.model
        entry = entry.lower()

        return (
            session.query(model.Customer)
            .filter(model.Customer.email_address.ilike(f"%{entry}%"))
            .all()
        )

    def search_customers_for_phone_number(self, session, entry, **kwargs):
        model = self.app.model
        entry = entry.lower()

        return (
            session.query(model.Customer)
            .filter(model.Customer.phone_number.ilike(f"%{entry}%"))
            .all()
        )

    def normalize_customer(self, customer):
        """
        Normalize the given customer to a JSON-serializable dict.
        """
        return {
            "uuid": customer.uuid,
            "customer_id": customer.customer_id,
            "name": customer.name,
            "phone_number": customer.phone_number,
            "email_address": customer.email_address,
            "_str": str(customer),
        }

    def get_customer_info_markdown(self, customer, **kwargs):
        """
        Returns a Markdown string containing pertinent info about a
        given customer account.
        """
        return (
            f"Customer ID: {customer.customer_id}\n\n"
            f"Name: {customer.name}\n\n"
            f"Phone: {customer.phone_number or ''}\n\n"
            f"Email: {customer.email_address or ''}\n\n"
        )
