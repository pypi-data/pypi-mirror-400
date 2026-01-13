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
WuttaPOS - txn item control
"""

import flet as ft


class WuttaTxnItem(ft.Row):
    """
    Control for displaying a transaction line item within main POS
    items list.
    """

    font_size = 24

    def __init__(self, config, row, page=None, *args, **kwargs):
        self.on_reset = kwargs.pop("on_reset", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = config.get_app()
        enum = self.app.enum

        self.row = row

        self.major_style = ft.TextStyle(size=self.font_size, weight=ft.FontWeight.BOLD)

        self.minor_style = ft.TextStyle(size=int(self.font_size * 0.8), italic=True)

        if self.row.row_type in (enum.POS_ROW_TYPE_SELL, enum.POS_ROW_TYPE_OPEN_RING):
            self.build_item_sell()

        # elif self.row.row_type in (self.enum.POS_ROW_TYPE_TENDER,
        #                            self.enum.POS_ROW_TYPE_CHANGE_BACK):
        #     self.build_item_tender()

    def build_item_sell(self):

        self.quantity = ft.TextSpan(style=self.minor_style)
        self.txn_price = ft.TextSpan(style=self.minor_style)

        self.sales_total_style = ft.TextStyle(
            size=self.font_size, weight=ft.FontWeight.BOLD
        )

        self.sales_total = ft.TextSpan(style=self.sales_total_style)

        self.fs_flag = ft.TextSpan(style=self.minor_style)
        self.tax_flag = ft.TextSpan(style=self.minor_style)

        # set initial text display values
        self.refresh(update=False)

        self.controls = [
            ft.Text(
                spans=[
                    ft.TextSpan(f"{self.row.description}", style=self.major_style),
                    ft.TextSpan("× ", style=self.minor_style),
                    self.quantity,
                    ft.TextSpan(" @ ", style=self.minor_style),
                    self.txn_price,
                ],
            ),
            ft.Text(
                spans=[
                    self.fs_flag,
                    self.tax_flag,
                    self.sales_total,
                ],
            ),
        ]
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def build_item_tender(self):
        self.controls = [
            ft.Text(
                spans=[
                    ft.TextSpan(f"{self.row.description}", style=self.major_style),
                ],
            ),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        self.app.render_currency(self.row.tender_total),
                        style=self.major_style,
                    ),
                ],
            ),
        ]
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def informed_refresh(self, **kwargs):
        pass

    def reset(self, e=None):
        if self.on_reset:
            self.on_reset(e=e)

    def refresh(self, update=True):
        enum = self.app.enum

        if self.row.void:
            self.major_style.color = None
            self.major_style.decoration = ft.TextDecoration.LINE_THROUGH
            self.major_style.weight = None
            self.minor_style.color = None
            self.minor_style.decoration = ft.TextDecoration.LINE_THROUGH
        else:
            self.major_style.color = None
            self.major_style.decoration = None
            self.major_style.weight = ft.FontWeight.BOLD
            self.minor_style.color = None
            self.minor_style.decoration = None

        if self.row.row_type in (enum.POS_ROW_TYPE_SELL, enum.POS_ROW_TYPE_OPEN_RING):
            self.quantity.text = self.app.render_quantity(self.row.quantity)
            self.txn_price.text = self.app.render_currency(self.row.txn_price)
            self.sales_total.text = self.app.render_currency(self.row.sales_total)
            self.fs_flag.text = "FS   " if self.row.foodstamp_eligible else ""
            self.tax_flag.text = f"T{self.row.tax_code}   " if self.row.tax_code else ""

            # if self.line.voided:
            if self.row.void:
                self.sales_total_style.color = None
                self.sales_total_style.decoration = ft.TextDecoration.LINE_THROUGH
                self.sales_total_style.weight = None
            else:
                if (
                    self.row.row_type == enum.POS_ROW_TYPE_SELL
                    and self.row.txn_price_adjusted
                ):
                    self.sales_total_style.color = "orange"
                elif (
                    self.row.row_type == enum.POS_ROW_TYPE_SELL
                    and self.row.cur_price
                    and self.row.cur_price < self.row.reg_price
                ):
                    self.sales_total_style.color = "green"
                else:
                    self.sales_total_style.color = None

                self.sales_total_style.decoration = None
                self.sales_total_style.weight = ft.FontWeight.BOLD

        if update:
            self.update()
