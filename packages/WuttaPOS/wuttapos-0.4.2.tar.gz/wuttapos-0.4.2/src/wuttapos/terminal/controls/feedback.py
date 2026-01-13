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
WuttaPOS - feedback control
"""

import time

import flet as ft

from .keyboard import WuttaKeyboard
from wuttapos.terminal.util import show_snackbar


class WuttaFeedback(ft.Container):

    default_font_size = 20
    default_button_height = 60

    def __init__(self, config, page=None, *args, **kwargs):
        self.on_reset = kwargs.pop("on_reset", None)
        self.on_send = kwargs.pop("on_send", None)
        self.on_cancel = kwargs.pop("on_cancel", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = config.get_app()
        self.enum = self.app.enum

        # TODO: why must we save this aside from self.page ?
        # but sometimes self.page gets set to None, so we must..
        self.mypage = page

        self.content = ft.Text(
            "Feedback", size=self.default_font_size, weight=ft.FontWeight.BOLD
        )
        self.height = self.default_button_height
        self.width = self.default_button_height * 3
        self.on_click = self.initial_click
        self.alignment = ft.alignment.center
        self.border = ft.border.all(1, "black")
        self.border_radius = ft.border_radius.all(5)
        self.bgcolor = "blue"

    def informed_refresh(self, **kwargs):
        pass

    def reset(self, e=None):
        if self.on_reset:
            self.on_reset(e=e)

    def initial_click(self, e):

        self.message = ft.TextField(
            label="Message", multiline=True, min_lines=5, autofocus=True
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("User Feedback"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Questions, suggestions, comments, complaints, etc. "
                            "are welcome and may be submitted below. "
                        ),
                        ft.Divider(),
                        self.message,
                        ft.Divider(),
                        WuttaKeyboard(
                            self.config,
                            on_keypress=self.keypress,
                            on_long_backspace=self.long_backspace,
                        ),
                    ],
                    expand=True,
                ),
                height=800,
            ),
            actions=[
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                "Send Message",
                                size=self.default_font_size,
                                color="black",
                                weight=ft.FontWeight.BOLD,
                            ),
                            height=self.default_button_height,
                            width=self.default_button_height * 3,
                            alignment=ft.alignment.center,
                            bgcolor="blue",
                            border=ft.border.all(1, "black"),
                            border_radius=ft.border_radius.all(5),
                            on_click=self.send_feedback,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Cancel",
                                size=self.default_font_size,
                                weight=ft.FontWeight.BOLD,
                            ),
                            height=self.default_button_height,
                            width=self.default_button_height * 2.5,
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "black"),
                            border_radius=ft.border_radius.all(5),
                            on_click=self.cancel,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

        # # TODO: leaving this for reference just in case..but hoping
        # the latest flet does not require this hack?

        # if self.mypage.dialog and self.mypage.dialog.open and self.mypage.dialog is not self.dlg:
        #     self.mypage.dialog.open = False
        #     self.mypage.update()
        #     # cf. https://github.com/flet-dev/flet/issues/1670
        #     time.sleep(0.1)

        # self.mypage.open(self.dlg)

        self.mypage.dialog = self.dlg
        self.dlg.open = True
        self.mypage.update()

    def keypress(self, key):
        if key == "⏎":
            self.message.value += "\n"
        elif key == "⌫":
            self.message.value = self.message.value[:-1]
        else:
            self.message.value += key

        self.message.focus()

        # TODO: why is keypress happening with no page?
        if self.page:
            self.update()

    def long_backspace(self):
        self.message.value = self.message.value[:-10]
        self.message.focus()
        self.update()

    def cancel(self, e):
        self.dlg.open = False
        self.mypage.update()

        if self.on_cancel:
            self.on_cancel(e)

    def send_feedback(self, e):
        if self.message.value:

            self.app.send_email(
                "pos_feedback",
                {
                    "user_name": self.mypage.session.get("user_display"),
                    "referrer": self.mypage.route,
                    "message": self.message.value,
                },
            )

            self.dlg.open = False
            show_snackbar(self.mypage, "MESSAGE WAS SENT", bgcolor="green")
            self.mypage.update()

            if self.on_send:
                self.on_send()

        else:
            self.message.focus()
            self.mypage.update()
