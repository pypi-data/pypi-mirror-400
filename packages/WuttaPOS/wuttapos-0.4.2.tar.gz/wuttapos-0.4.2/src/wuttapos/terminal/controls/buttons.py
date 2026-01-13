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
WuttaPOS - buttons
"""

import flet as ft


def make_button(text, font_size=24, font_bold=True, font_weight=None, **kwargs):
    """
    Generic function for making a button.
    """
    if "content" not in kwargs:
        if not font_weight and font_bold:
            font_weight = ft.FontWeight.BOLD
        text = ft.Text(
            text, size=font_size, weight=font_weight, text_align=ft.TextAlign.CENTER
        )
        kwargs["content"] = text

    return WuttaButton(**kwargs)


class WuttaButton(ft.Container):
    """
    Base class for buttons to be shown in the POS menu etc.
    """

    def __init__(
        self,
        pos=None,
        pos_cmd=None,
        pos_cmd_entry=None,
        pos_cmd_kwargs={},
        *args,
        **kwargs
    ):
        kwargs.setdefault("alignment", ft.alignment.center)
        kwargs.setdefault("border", ft.border.all(1, "black"))
        kwargs.setdefault("border_radius", ft.border_radius.all(5))
        super().__init__(*args, **kwargs)

        self.pos = pos
        self.pos_cmd = pos_cmd
        self.pos_cmd_entry = pos_cmd_entry
        self.pos_cmd_kwargs = pos_cmd_kwargs

        if not kwargs.get("on_click") and self.pos and self.pos_cmd:
            self.on_click = self.handle_click

    def handle_click(self, e):
        self.pos.cmd(self.pos_cmd, entry=self.pos_cmd_entry, **self.pos_cmd_kwargs)


class WuttaButtonRow(ft.Row):
    """
    Base class for a row of buttons
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("spacing", 0)
        super().__init__(*args, **kwargs)
