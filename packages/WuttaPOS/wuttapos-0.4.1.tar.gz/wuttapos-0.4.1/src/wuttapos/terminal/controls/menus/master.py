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
WuttaPOS - menus master control
"""

import flet as ft

from wuttapos.terminal.controls.menus.tenkey import WuttaTenkeyMenu
from wuttapos.terminal.controls.menus.meta import WuttaMetaMenu
from wuttapos.terminal.controls.menus.suspend import WuttaSuspendMenu


class WuttaMenuMaster(ft.Column):
    """
    Base class and default implementation for "buttons master"
    control.  This represents the overall button area in POS view.
    """

    def __init__(self, config, pos=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.app = self.config.get_app()
        self.pos = pos
        self.controls = self.build_controls()

    def build_controls(self):
        self.tenkey_menu = self.build_tenkey_menu()
        self.meta_menu = self.build_meta_menu()
        self.context_menu = self.build_context_menu()
        self.suspend_menu = self.build_suspend_menu()

        return [
            ft.Row(
                [
                    self.tenkey_menu,
                    self.meta_menu,
                ],
            ),
            ft.Row(
                [
                    self.context_menu,
                    self.suspend_menu,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ]

    ##############################
    # tenkey
    ##############################

    def build_tenkey_menu(self):
        return WuttaTenkeyMenu(
            self.config,
            pos=self.pos,
            on_char=self.tenkey_char,
            on_enter=self.tenkey_enter,
            on_up_click=self.tenkey_up_click,
            on_up_longpress=self.tenkey_up_longpress,
            on_down_click=self.tenkey_down_click,
            on_down_longpress=self.tenkey_down_longpress,
        )

    def tenkey_char(self, key):
        self.pos.cmd("entry_append", key)

    def tenkey_enter(self, e):
        self.pos.cmd("entry_submit")

    def tenkey_up_click(self, e):
        self.pos.cmd("scroll_up")

    def tenkey_up_longpress(self, e):
        self.pos.cmd("scroll_up_page")

    def tenkey_down_click(self, e):
        self.pos.cmd("scroll_down")

    def tenkey_down_longpress(self, e):
        self.pos.cmd("scroll_down_page")

    ##############################
    # meta
    ##############################

    def build_meta_menu(self):
        return WuttaMetaMenu(self.config, pos=self.pos)

    ##############################
    # context
    ##############################

    def build_context_menu(self):
        spec = self.config.get(
            "wuttapos.menus.context.spec",
            default="wuttapos.terminal.controls.menus.context:WuttaContextMenu",
        )
        factory = self.app.load_object(spec)
        return factory(self.config, pos=self.pos)

    def replace_context_menu(self, menu):
        controls = menu.build_controls()
        self.context_menu.content.controls = controls
        self.update()

    ##############################
    # suspend
    ##############################

    def build_suspend_menu(self):
        return WuttaSuspendMenu(self.config, pos=self.pos)
