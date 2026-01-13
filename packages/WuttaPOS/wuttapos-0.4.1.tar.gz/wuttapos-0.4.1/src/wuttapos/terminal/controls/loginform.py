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
WuttaPOS - login form control
"""

import logging

import flet as ft

from wuttapos.terminal.controls.buttons import make_button
from wuttapos.terminal.controls.keyboard import WuttaKeyboard
from wuttapos.terminal.controls.menus.tenkey import WuttaTenkeyMenu


log = logging.getLogger(__name__)


class WuttaLoginForm(ft.Column):

    def __init__(self, config, page=None, pos=None, *args, **kwargs):
        self.on_reset = kwargs.pop("on_reset", None)

        # permission to be checked for login to succeed
        self.perm_required = kwargs.pop("perm_required", "pos.ring_sales")

        # may or may not show the username field
        # nb. must set this before normal __init__
        if "show_username" in kwargs:
            self.show_username = kwargs.pop("show_username")
        else:
            self.show_username = config.get_bool(
                "wuttapos.login.show_username", default=True
            )

        # may or may not show 10-key menu instead of full keyboard
        if "use_tenkey" in kwargs:
            self.use_tenkey = kwargs.pop("use_tenkey")
        else:
            self.use_tenkey = config.get_bool(
                "wuttapos.login.use_tenkey", default=False
            )

        self.on_login_failure = kwargs.pop("on_login_failure", None)
        self.on_authz_failure = kwargs.pop("on_authz_failure", None)
        self.on_login_success = kwargs.pop("on_login_success", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = config.get_app()
        self.enum = self.app.enum
        self.pos = pos

        # track which login input has focus
        self.focused = None

        login_form = self.build_login_form()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER

        if self.use_tenkey:
            self.controls = [
                ft.Row(
                    [
                        login_form,
                        ft.VerticalDivider(),
                        WuttaTenkeyMenu(
                            self.config,
                            pos=self.pos,
                            simple=True,
                            on_char=self.tenkey_char,
                            on_enter=self.tenkey_enter,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]

        else:  # full keyboard
            self.controls = [
                login_form,
                ft.Row(),
                ft.Row(),
                ft.Row(),
                WuttaKeyboard(
                    self.config,
                    on_keypress=self.keyboard_keypress,
                    on_long_backspace=self.keyboard_long_backspace,
                ),
            ]

    def informed_refresh(self, **kwargs):
        pass

    def reset(self, e=None):
        if self.on_reset:
            self.on_reset(e=e)

    def build_login_form(self):
        form_fields = []

        self.password = ft.TextField(
            label="Password",
            width=200,
            password=True,
            on_submit=self.password_submit,
            on_focus=self.password_focus,
            autofocus=not self.show_username,
        )
        self.focused = self.password

        if self.show_username:
            self.username = ft.TextField(
                label="Login",
                width=200,
                on_submit=self.username_submit,
                on_focus=self.username_focus,
                autofocus=True,
            )
            form_fields.append(self.username)
            self.focused = self.username

        form_fields.append(self.password)

        login_button = make_button(
            "Login",
            height=60,
            width=60 * 2.5,
            bgcolor="blue",
            on_click=self.attempt_login,
        )

        reset_button = make_button(
            "Clear", height=60, width=60 * 2.5, on_click=self.clear_login
        )

        if self.use_tenkey:
            form_fields.extend(
                [
                    ft.Row(),
                    ft.Row(),
                    ft.Row(
                        [
                            reset_button,
                            login_button,
                        ],
                    ),
                ]
            )
            return ft.Column(
                controls=form_fields,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        else:  # full keyboard
            form_fields.extend(
                [
                    login_button,
                    reset_button,
                ]
            )
            return ft.Row(
                controls=form_fields,
                alignment=ft.MainAxisAlignment.CENTER,
            )

    def keyboard_keypress(self, key):
        assert self.focused

        if key == "⏎":  # ENTER

            # attempt to submit the login form..
            if self.show_username and self.focused is self.username:
                self.username_submit()
            else:
                if self.password_submit():

                    # here the login has totally worked, which means
                    # this form has fulfilled its purpose.  hence must
                    # exit early to avoid update() in case we are to
                    # be redirected etc.  otherwise may get errors
                    # trying to update controls which have already
                    # been dropped from the page..
                    return

        elif key == "⌫":
            self.focused.value = self.focused.value[:-1]

        else:
            self.focused.value += key

        self.focused.focus()
        self.update()

    def keyboard_long_backspace(self):
        assert self.focused
        self.focused.value = ""
        self.focused.focus()
        self.update()

    def tenkey_char(self, key):
        if key == "@":
            return

        self.focused.value = f"{self.focused.value or ''}{key}"
        self.update()

    def tenkey_enter(self, e):
        if self.show_username and self.focused is self.username:
            self.username_submit(e)
            self.update()
        else:
            if not self.password_submit(e):
                self.update()

    def username_focus(self, e):
        self.focused = self.username

    def username_submit(self, e=None):
        if self.username.value:
            self.password.focus()
        else:
            self.username.focus()

    def password_focus(self, e):
        self.focused = self.password

    def password_submit(self, e=None):
        if self.password.value:
            return self.attempt_login(e)
        else:
            self.password.focus()
            return False

    def attempt_login(self, e=None):
        if self.show_username and not self.username.value:
            self.username.focus()
            return False
        if not self.password.value:
            self.password.focus()
            return False

        session = self.app.make_session()
        auth = self.app.get_auth_handler()
        try:
            user = auth.authenticate_user(
                session,
                self.username.value if self.show_username else None,
                self.password.value,
            )
        except:
            log.exception("user authentication error")
            session.close()
            if self.on_login_failure:
                self.on_login_failure(e)
            self.clear_login()
            return False

        user_display = str(user) if user else None
        has_perm = (
            auth.has_permission(session, user, self.perm_required) if user else False
        )
        session.close()

        if user:

            if has_perm:
                if self.on_login_success:
                    self.on_login_success(user, user_display)
                return True

            else:
                if self.on_authz_failure:
                    self.on_authz_failure(user, user_display)
                self.clear_login()

        else:
            if self.on_login_failure:
                self.on_login_failure(e)
            self.clear_login()

        return False

    def clear_login(self, e=None):
        if self.show_username:
            self.username.value = ""
        self.password.value = ""
        if self.show_username:
            self.username.focus()
        else:
            self.password.focus()
        self.update()
