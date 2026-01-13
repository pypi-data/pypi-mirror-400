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
WuttaPOS - transaction lookup control
"""

from .lookup import WuttaLookup


class WuttaTransactionLookup(WuttaLookup):

    def __init__(self, *args, **kwargs):

        # nb. this forces first query
        kwargs.setdefault("initial_search", True)

        # TODO: how to deal with 'modes'
        self.mode = kwargs.pop("mode", None)
        if not self.mode:
            raise ValueError("must specify mode")
        if self.mode != "resume":
            raise ValueError("only 'resume' mode is supported")

        kwargs.setdefault("show_search", False)

        super().__init__(*args, **kwargs)

    def get_results_columns(self):
        return [
            "Created",
            "Terminal",
            "Txn ID",
            "Cashier",
            "Customer",
            "Balance",
        ]

    def get_results(self, session, entry):
        model = self.app.model

        # TODO: how to deal with 'modes'
        assert self.mode == "resume"
        training = bool(self.mypage.session.get("training"))
        query = (
            session.query(model.POSBatch)
            .filter(model.POSBatch.status_code == model.POSBatch.STATUS_SUSPENDED)
            .filter(model.POSBatch.executed == None)
            .filter(model.POSBatch.training_mode == training)
            .order_by(model.POSBatch.created.desc())
        )

        transactions = []
        for batch in query:
            transactions.append(
                {
                    "uuid": batch.uuid,
                    "created": self.app.render_datetime(batch.created),
                    "terminal": batch.terminal.terminal_id,
                    "txnid": batch.id_str,
                    "cashier": batch.cashier.name,
                    "customer": batch.customer.name,
                    "balance": self.app.render_currency(batch.get_balance()),
                }
            )
        return transactions

    def make_result_row(self, txn):
        return [
            txn["created"],
            txn["terminal"],
            txn["txnid"],
            txn["cashier"],
            txn["customer"],
            txn["balance"],
        ]
