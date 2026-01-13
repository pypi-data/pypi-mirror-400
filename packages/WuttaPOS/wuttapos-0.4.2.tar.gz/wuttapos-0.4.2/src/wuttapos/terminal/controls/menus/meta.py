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
WuttaPOS - "meta" menu
"""

from .base import WuttaMenu


class WuttaMetaMenu(WuttaMenu):

    def build_controls(self):
        return [
            self.make_button_row(
                [
                    self.make_button("CUST", bgcolor="blue", pos_cmd="customer_dwim"),
                    self.make_button("VOID", bgcolor="red", pos_cmd="void_dwim"),
                ]
            ),
            self.make_button_row(
                [
                    self.make_button("ITEM", bgcolor="blue", pos_cmd="item_dwim"),
                    self.make_button("MGR", bgcolor="yellow", pos_cmd="manager_dwim"),
                ]
            ),
            self.make_button_row(
                [
                    self.make_button(
                        "OPEN RING",
                        font_size=32,
                        bgcolor="blue",
                        pos_cmd="open_ring_dwim",
                    ),
                    self.make_button(
                        "NO SALE", bgcolor="yellow", pos_cmd="no_sale_dwim"
                    ),
                ]
            ),
            self.make_button_row(
                [
                    self.make_button(
                        "Adjust\nPrice",
                        font_size=30,
                        bgcolor="yellow",
                        pos_cmd="adjust_price_dwim",
                    ),
                    self.make_button("REFUND", bgcolor="red", pos_cmd="refund_dwim"),
                ]
            ),
        ]
