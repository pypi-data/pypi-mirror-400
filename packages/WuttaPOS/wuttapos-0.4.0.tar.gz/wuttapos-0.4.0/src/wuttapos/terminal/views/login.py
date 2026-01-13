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
WuttaPOS - login view
"""

import flet as ft

from .base import WuttaView
from wuttapos.terminal.controls.loginform import WuttaLoginForm


class LoginView(WuttaView):
    """
    Main POS view for WuttaPOS
    """

    def build_controls(self):
        title = self.app.get_title()

        controls = [
            ft.Row(
                [self.make_logo_image(height=200)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    ft.Text(
                        value=f"Welcome to {title}", weight=ft.FontWeight.BOLD, size=28
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(),
            ft.Row(),
            ft.Row(),
            WuttaLoginForm(
                self.config,
                on_login_failure=self.login_failure,
                on_authz_failure=self.authz_failure,
                on_login_success=self.login_success,
            ),
        ]

        return [
            self.build_header(),
            ft.Column(
                controls=controls, expand=True, alignment=ft.MainAxisAlignment.CENTER
            ),
        ]

    def login_failure(self, e):
        self.show_snackbar("Login failed!", bgcolor="yellow")
        self.page.update()

    def authz_failure(self, user, user_display):
        self.show_snackbar(
            f"User not allowed to ring sales: {user_display}", bgcolor="yellow"
        )
        self.page.update()

    def login_success(self, user, user_display):
        self.page.session.set("user_uuid", user.uuid.hex)
        self.page.session.set("user_display", user_display)

        # TODO: hacky but works for now
        if not self.config.production():
            self.page.client_storage.set("user_uuid", user.uuid.hex)

        self.page.go("/pos")
