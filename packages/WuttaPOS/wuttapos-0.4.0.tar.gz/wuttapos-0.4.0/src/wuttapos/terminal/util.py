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
WuttaPOS utilities
"""

import flet as ft


def show_snackbar(page, text, bgcolor="yellow"):
    snack_bar = ft.SnackBar(
        ft.Text(text, color="black", size=40, weight=ft.FontWeight.BOLD),
        bgcolor=bgcolor,
        duration=1500,
    )
    page.overlay.append(snack_bar)
    snack_bar.open = True


def get_pos_batch_handler(config):
    """
    Official way of obtaining the POS batch handler.

    Code should use this where possible to make later refactoring
    easier, should it be needed.
    """
    app = config.get_app()
    return app.get_batch_handler("pos", default="wuttapos.batch.pos:POSBatchHandler")
