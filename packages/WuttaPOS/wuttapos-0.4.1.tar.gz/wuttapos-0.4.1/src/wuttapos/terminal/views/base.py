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
WuttaPOS - flet views (base class)
"""

import os

from wuttjamaican.util import resource_path

import flet as ft

from wuttapos.terminal.controls.header import WuttaHeader
from wuttapos.terminal.controls.buttons import make_button
from wuttapos.terminal.util import show_snackbar, get_pos_batch_handler


class WuttaView(ft.View):
    """
    Base class for all Flet views used in WuttaPOS
    """

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.app = self.config.get_app()

        controls = self.build_controls()
        self.controls = [
            WuttaViewContainer(
                self.config, content=ft.Column(controls=controls), expand=True
            ),
        ]

    def build_controls(self):
        return [self.build_header()]

    def build_header(self):
        handler = self.get_batch_handler()
        self.header = WuttaHeader(
            self.config, on_reset=self.reset, terminal_id=handler.get_terminal_id()
        )
        return self.header

    def get_batch_handler(self):
        return get_pos_batch_handler(self.config)

    def make_button(self, *args, **kwargs):
        return make_button(*args, **kwargs)

    def reset(self, *args, **kwargs):
        pass

    def make_logo_image(self, **kwargs):

        # we have a default header logo, but prefer custom if present
        custom = resource_path("wuttapos.terminal:assets/custom_header_logo.png")
        if os.path.exists(custom):
            logo = "/custom_header_logo.png"
        else:
            logo = "/header_logo.png"

        # but config can override in any case
        logo = self.config.get("wuttapos.header.logo", default=logo)

        kwargs.setdefault("height", 100)
        return ft.Image(src=logo, **kwargs)

    def show_snackbar(self, text, bgcolor="yellow"):
        show_snackbar(self.page, text, bgcolor=bgcolor)


class WuttaViewContainer(ft.Container):
    """
    Main container class to wrap all controls for a view.  Used for
    displaying background image etc.
    """

    def __init__(self, config, *args, **kwargs):
        self.config = config

        # # add testing watermark when not in production
        # if "image_src" not in kwargs and not self.config.production():
        #     kwargs["image_src"] = "/testing.png"
        #     kwargs.setdefault("image_repeat", ft.ImageRepeat.REPEAT)

        super().__init__(*args, **kwargs)
