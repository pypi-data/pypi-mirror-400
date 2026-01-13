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
WuttaPOS - keyboard control
"""

import flet as ft


class WuttaKeyboard(ft.Container):

    default_font_size = 20
    default_button_size = 80

    def __init__(self, config, page=None, *args, **kwargs):
        self.on_reset = kwargs.pop("on_reset", None)
        self.on_keypress = kwargs.pop("on_keypress", None)
        self.on_long_backspace = kwargs.pop("on_long_backspace", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = config.get_app()
        self.enum = self.app.enum

        self.caps_lock = False
        self.caps_map = dict([(k, k.upper()) for k in "abcdefghijklmnopqrstuvwxyz"])

        self.shift = False
        self.shift_map = {
            "`": "~",
            "1": "!",
            "2": "@",
            "3": "#",
            "4": "$",
            "5": "%",
            "6": "^",
            "7": "&",
            "8": "*",
            "9": "(",
            "0": ")",
            "-": "_",
            "=": "+",
            "[": "{",
            "]": "}",
            "\\": "|",
            ";": ":",
            "'": '"',
            ",": "<",
            ".": ">",
            "/": "?",
        }

        self.keys = {}

        def make_key(
            key,
            data=None,
            on_click=self.simple_keypress,
            on_long_press=None,
            width=self.default_button_size,
            bgcolor=None,
        ):
            button = ft.Container(
                content=ft.Text(
                    key, size=self.default_font_size, weight=ft.FontWeight.BOLD
                ),
                data=data or key,
                height=self.default_button_size,
                width=width,
                on_click=on_click,
                on_long_press=on_long_press,
                alignment=ft.alignment.center,
                border=ft.border.all(1, "black"),
                border_radius=ft.border_radius.all(5),
                bgcolor=bgcolor,
            )
            self.keys[key] = button
            return button

        def caps_click(e):
            self.update_caps_lock(not self.caps_lock)

        self.caps_key = make_key("CAPS", on_click=caps_click)
        if self.caps_lock:
            self.caps_key.bgcolor = "blue"

        def shift_click(e):
            self.update_shift(not self.shift)

        self.shift_key = make_key("SHIFT", on_click=shift_click)
        if self.shift:
            self.shift_key.bgcolor = "blue"

        rows = [
            [make_key(k) for k in "`1234567890-="]
            + [make_key("⌫", bgcolor="yellow", on_long_press=self.long_backspace)],
            [make_key(k) for k in "qwertyuiop[]\\"],
            [self.caps_key]
            + [make_key(k) for k in "asdfghjkl;'"]
            + [make_key("⏎", bgcolor="blue")],
            [self.shift_key] + [make_key(k) for k in "zxcvbnm,./"],
            [make_key("SPACE", width=self.default_button_size * 5)],
        ]

        rows = [
            ft.Row(controls, alignment=ft.MainAxisAlignment.CENTER) for controls in rows
        ]

        self.content = ft.Column(rows)

    def informed_refresh(self, **kwargs):
        pass

    def reset(self, e=None):
        if self.on_reset:
            self.on_reset(e=e)

    def update_caps_lock(self, caps_lock):
        self.caps_lock = caps_lock

        if self.caps_lock:
            self.caps_key.bgcolor = "blue"
        else:
            self.caps_key.bgcolor = None

        for key, button in self.keys.items():
            if key in self.caps_map:
                if self.caps_lock or self.shift:
                    button.content.value = self.caps_map[key]
                else:
                    button.content.value = key

        self.update()

    def update_shift(self, shift):
        self.shift = shift

        if self.shift:
            self.shift_key.bgcolor = "blue"
        else:
            self.shift_key.bgcolor = None

        for key, button in self.keys.items():
            if key in self.caps_map:
                if self.shift or self.caps_lock:
                    button.content.value = self.caps_map[key]
                else:
                    button.content.value = key
            elif key in self.shift_map:
                if self.shift:
                    button.content.value = self.shift_map[key]
                else:
                    button.content.value = key

        self.update()

    def simple_keypress(self, e):

        # maybe inform parent
        if self.on_keypress:
            key = e.control.content.value

            # avoid callback for certain keys
            if key not in ("CAPS", "SHIFT"):

                # translate certain keys
                if key == "SPACE":
                    key = " "

                # let 'em know
                self.on_keypress(key)

        # turn off shift key if set
        if self.shift:
            self.update_shift(False)

    def long_backspace(self, e):
        if self.on_long_backspace:
            self.on_long_backspace()
