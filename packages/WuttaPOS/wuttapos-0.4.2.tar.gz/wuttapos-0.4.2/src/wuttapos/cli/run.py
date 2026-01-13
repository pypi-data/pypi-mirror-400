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
See also: :ref:`wuttapos-run`
"""

import os

import typer

from wuttapos.cli import wuttapos_typer


@wuttapos_typer.command()
def run(ctx: typer.Context):
    """
    Run the WuttaPOS GUI app
    """
    from wuttapos.terminal.app import run_app

    config = ctx.parent.wutta_config

    # nb. it does not seem possible (?) to inject our config when
    # launching the Flet app, which means it will create a *separate*
    # config for itself..this should ensure it has the right settings.
    # see also notes in wuttapos.terminal.app module, for run_app()
    os.environ["WUTTA_CONFIG_FILES"] = os.pathsep.join(config.get_prioritized_files())

    run_app()
