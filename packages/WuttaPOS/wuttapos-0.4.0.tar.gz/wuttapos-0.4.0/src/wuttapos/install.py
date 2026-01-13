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
Install handler for WuttaPOS
"""

import subprocess
import sys

from wuttjamaican import install as base


class InstallHandler(base.InstallHandler):
    """
    Custom install handler for WuttaPOS
    """

    template_paths = ["wuttapos:installer-templates"]

    def do_install_steps(self):

        # prompt for install type first
        self.get_install_type()

        # then everything else
        super().do_install_steps()

    def get_install_type(self):

        # prompt user
        install_type = None
        while install_type not in ("server", "terminal"):
            install_type = self.prompt_generic("install type (server/terminal)")

        # remember the answer
        self.install_type = install_type

        if self.install_type != "server":
            self.rprint(
                "[bold red]sorry, terminal install is not yet implemented[/bold red]\n"
            )
            sys.exit(1)

        # install dependencies
        if self.install_type == "server":
            self.install_server_deps()

    def install_server_deps(self):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "WuttaPOS[server]"]
        )

    def make_template_context(self, dbinfo, **kwargs):
        context = super().make_template_context(dbinfo, **kwargs)
        context["install_type"] = self.install_type
        return context
