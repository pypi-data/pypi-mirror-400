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
WuttaPOS - header control
"""

import datetime

import flet as ft

import wuttapos
from .timestamp import WuttaTimestamp
from .feedback import WuttaFeedback
from wuttapos.terminal.controls.buttons import make_button


class WuttaHeader(ft.Stack):

    def __init__(self, config, page=None, *args, **kwargs):
        self.terminal_id = kwargs.pop("terminal_id", None)
        self.on_reset = kwargs.pop("on_reset", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = config.get_app()
        self.enum = self.app.enum

        self.txn_display = ft.Text("Txn: N", weight=ft.FontWeight.BOLD, size=20)
        self.cust_display = ft.Text("Cust: N", weight=ft.FontWeight.BOLD, size=20)

        self.training_mode = ft.Text(size=40, weight=ft.FontWeight.BOLD)

        self.user_display = ft.Text("User: N", weight=ft.FontWeight.BOLD, size=20)
        self.logout_button = ft.OutlinedButton(
            "Logout", on_click=self.logout_click, visible=False
        )
        self.logout_divider = ft.VerticalDivider(visible=False)
        self.title_button = ft.FilledButton(
            self.app.get_title(), on_click=self.title_click
        )

        terminal_style = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)
        if not self.terminal_id:
            terminal_style.bgcolor = "red"
            terminal_style.color = "white"

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=self.training_mode,
                            bgcolor="yellow",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
            ft.Row(
                [
                    ft.Row(
                        [
                            self.txn_display,
                            ft.VerticalDivider(),
                            self.cust_display,
                            ft.VerticalDivider(),
                            WuttaTimestamp(
                                self.config, weight=ft.FontWeight.BOLD, size=20
                            ),
                        ],
                    ),
                    ft.Row(
                        [
                            self.user_display,
                            ft.VerticalDivider(),
                            self.logout_button,
                            self.logout_divider,
                            ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        style=terminal_style,
                                        text=f"Term: {self.terminal_id or '??'}",
                                    ),
                                ],
                            ),
                            ft.VerticalDivider(),
                            self.title_button,
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]

    def reset(self, e=None):
        if self.on_reset:
            self.on_reset(e=e)

    def did_mount(self):
        self.informed_refresh()

    def informed_refresh(self):
        self.update_txn_display()
        self.update_cust_display()
        self.update_user_display()
        self.update_training_display()
        self.update()

    def update_txn_display(self):
        txn_display = None
        if self.page:
            txn_display = self.page.session.get("txn_display")
        self.txn_display.value = f"Txn: {txn_display or 'N'}"

    def update_cust_display(self):
        cust_display = None
        if self.page:
            cust_display = self.page.session.get("cust_display")
        self.cust_display.value = f"Cust: {cust_display or 'N'}"

    def update_training_display(self):
        if self.page.session.get("training"):
            self.training_mode.value = "  TRAINING MODE  "
        else:
            self.training_mode.value = ""

    def update_user_display(self):
        user_display = None
        if self.page:
            user_display = self.page.session.get("user_display")
        self.user_display.value = f"User: {user_display or 'N'}"

        if self.page and self.page.session.get("user_uuid"):
            self.logout_button.visible = True
            self.logout_divider.visible = True

    def logout_click(self, e):

        # TODO: hacky but works for now
        if not self.config.production():
            self.page.client_storage.set("user_uuid", "")

        self.page.session.clear()
        self.page.go("/login")

    def title_click(self, e):
        title = self.app.get_title()

        year = self.app.localtime().year
        if year > 2026:
            year_range = f"2026 - {year}"
        else:
            year_range = year

        license = f"""\
WuttaPOS -- Point of Sale system based on Wutta Framework
Copyright © {year_range} Lance Edgar

WuttaPOS is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

WuttaPOS is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
WuttaPOS.  If not, see <http://www.gnu.org/licenses/>.
"""

        buttons = []

        user_uuid = self.page.session.get("user_uuid")
        if user_uuid:

            session = self.app.make_session()
            model = self.app.model
            user = session.get(model.User, user_uuid)
            auth = self.app.get_auth_handler()
            has_perm = auth.has_permission(session, user, "pos.test_error")
            session.close()
            if has_perm:
                test_error = make_button(
                    "TEST ERROR",
                    font_size=24,
                    height=60,
                    width=60 * 3,
                    bgcolor="red",
                    on_click=self.test_error_click,
                )
                buttons.append(test_error)

            feedback = WuttaFeedback(
                self.config, page=self.page, on_send=self.reset, on_cancel=self.reset
            )
            buttons.append(feedback)

        self.dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Divider(),
                        ft.Text(f"{title} v{wuttapos.__version__}"),
                        ft.Divider(),
                        ft.Text(license),
                        ft.Container(
                            content=ft.Row(
                                controls=buttons,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                    ],
                    expand=True,
                ),
                height=600,
            ),
            actions=[
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                "Close", size=20, weight=ft.FontWeight.BOLD
                            ),
                            height=60,
                            width=60 * 2.5,
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "black"),
                            border_radius=ft.border_radius.all(5),
                            on_click=self.close_dlg,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

        # self.page.open(self.dlg)

        self.page.dialog = self.dlg
        self.dlg.open = True
        self.page.update()

    def test_error_click(self, e):

        # first get the dialog out of the way
        self.dlg.open = False
        self.reset()
        self.page.update()

        raise RuntimeError("FAKE ERROR - to test error handling")

    def close_dlg(self, e):
        self.dlg.open = False
        self.reset()
        self.page.update()
