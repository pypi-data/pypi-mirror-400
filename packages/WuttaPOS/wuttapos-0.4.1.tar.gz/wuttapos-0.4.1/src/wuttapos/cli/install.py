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
WuttaPOS CLI
"""

import typer

from wuttapos.cli import wuttapos_typer


@wuttapos_typer.command()
def install(
    ctx: typer.Context,
):
    """
    Install the server app
    """
    config = ctx.parent.wutta_config
    app = config.get_app()
    install = app.get_install_handler(
        pkg_name="wuttapos",
        app_title="WuttaPOS",
        pypi_name="WuttaPOS",
        egg_name="WuttaPOS",
    )
    install.run()
