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
WuttaPOS - button menus
"""

import flet as ft

from wuttapos.terminal.controls.buttons import make_button, WuttaButtonRow


class WuttaMenu(ft.Container):
    """
    Base class for button menu controls.
    """

    # TODO: should be configurable somehow
    default_button_size = 100
    default_font_size = 40

    def __init__(self, config, pos=None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = self.config.get_app()
        self.pos = pos

        self.content = ft.Column(controls=self.build_controls(), spacing=0)

    def make_button(self, *args, **kwargs):
        kwargs.setdefault("font_size", self.default_font_size)
        kwargs.setdefault("height", self.default_button_size)
        kwargs.setdefault("width", self.default_button_size * 2)
        kwargs.setdefault("pos", self.pos)
        return make_button(*args, **kwargs)

    def make_button_row(self, *args, **kwargs):
        return WuttaButtonRow(*args, **kwargs)
