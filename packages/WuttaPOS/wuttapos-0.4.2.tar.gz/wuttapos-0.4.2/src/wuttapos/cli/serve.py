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
See also: :ref:`wuttapos-serve`
"""

import logging

import typer

from wuttapos.cli import wuttapos_typer
from wuttjamaican.util import resource_path


log = logging.getLogger(__name__)


@wuttapos_typer.command()
def serve(ctx: typer.Context):
    """
    Run the WuttaPOS web service
    """
    import flet as ft
    from wuttapos.terminal.app import main

    config = ctx.parent.wutta_config
    kw = {}

    host = config.get("wuttapos.serve.host", default="0.0.0.0")
    kw["host"] = host

    port = config.get_int("wuttapos.serve.port", default=8332)
    kw["port"] = port

    # TODO: we technically "support" this, in that we do pass the
    # value on to Flet, but in practice it does not work right
    path = config.get("wuttapos.serve.path", default="")
    if path:
        path = path.strip("/") + "/"
        kw["name"] = path
        # kw['route_url_strategy'] = 'hash'

    log.info(f"will serve WuttaPOS on http://{host}:{port}/{path}")
    ft.app(
        target=main,
        view=None,
        assets_dir=resource_path("wuttapos.terminal:assets"),
        **kw,
    )
