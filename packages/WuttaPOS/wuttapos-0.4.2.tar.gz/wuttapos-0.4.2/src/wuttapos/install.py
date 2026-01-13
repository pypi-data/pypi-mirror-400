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

import os
import subprocess
import sys

from wuttjamaican import install as base


class InstallHandler(base.InstallHandler):
    """
    Custom install handler for WuttaPOS
    """

    template_paths = ["wuttapos:installer-templates"]

    store_id = None
    terminal_id = None
    alongside = False

    def do_install_steps(self):

        # prompt for install type first
        self.get_install_type()

        # install server/terminal dependencies
        self.install_app_deps()

        # then everything else
        super().do_install_steps()

    def sanity_check(self):
        """
        We override this because the normal up-front sanity check
        includes a check for the app dir.  But we need to delay that
        one a bit, so behavior depends on which "install type" we're
        doing.
        """

    def check_appdir(self):
        """
        We bypass the normal check here, if the current install is for
        terminal alongside server.
        """
        if self.install_type == "terminal":

            # does appdir exist yet?
            appdir = os.path.join(sys.prefix, "app")
            if os.path.exists(appdir):

                # install alongside server?
                self.alongside = self.prompt_bool(
                    "install alongside server?", default=False
                )
                if self.alongside:
                    # this mode expects the appdir to exist, so continue
                    return

            else:
                # no appdir - means we should install "everything" for
                # the terminal, but we don't support that yet
                self.rprint(
                    f"\n\t[bold red]sorry, full terminal install not yet supported[/bold red]\n"
                )
                self.rprint(
                    f"\n\tPlease install the server, then terminal alongside that.\n"
                )
                sys.exit(2)

        # do normal check
        super().check_appdir()

    def get_install_type(self):

        # prompt user
        install_type = None
        while install_type not in ("server", "terminal"):
            install_type = self.prompt_generic("install type (server/terminal)")

        # remember the answer
        self.install_type = install_type

        # and skip the continuum prompt
        self.wants_continuum = install_type == "server"

        # now we can check the app dir; do this before further questions
        self.check_appdir()

        # stop here for server, but we have more questions for terminal
        if self.install_type == "server":
            return

        self.rprint(
            "\n\n\t[blue]Next you must specify the Store and Terminal IDs.[/blue]"
        )
        self.rprint(
            "\n\tThese should match records in your DB; see the Server app for info.\n"
        )

        # store_id
        while not self.store_id:
            self.store_id = self.prompt_generic("Store ID")

        # terminal_id
        while not self.terminal_id:
            self.terminal_id = self.prompt_generic("Terminal ID")

    def install_app_deps(self):

        if self.install_type == "server":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "WuttaPOS[server]"]
            )

        elif self.install_type == "terminal":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "WuttaPOS[terminal]"]
            )

    def get_db_url(self):
        if self.alongside:
            return self.config.appdb_engine.url

        return super().get_db_url()

    def make_template_context(self, **kwargs):
        context = super().make_template_context(**kwargs)

        context["install_type"] = self.install_type
        context["store_id"] = self.store_id
        context["terminal_id"] = self.terminal_id

        return context

    def write_all_config_files(self, appdir, context):
        if self.alongside:
            # just want to add terminal.conf for this mode
            self.write_terminal_conf(appdir, context)
            return

        # new app, so write normal files
        super().write_all_config_files(appdir, context)

    def write_terminal_conf(self, appdir, context):
        term_context = dict(context)
        self.make_config_file(
            "terminal.conf.mako", os.path.join(appdir, "terminal.conf"), **term_context
        )

    def install_db_schema(self, db_url, appdir=None):
        if self.alongside:
            # no need to install schema here
            return False

        return super().install_db_schema(db_url, appdir=appdir)

    def show_goodbye(self):
        """
        Show the final message; this assumes setup completed okay.

        This is normally called by :meth:`run()`.
        """
        if self.alongside:
            self.rprint("\n\t[bold green]initial setup is complete![/bold green]")
            self.rprint("\n\tyou can run the terminal GUI app with:")
            self.rprint(f"\n\t[blue]cd {sys.prefix}[/blue]")
            self.rprint("\t[blue]bin/wuttapos -c app/terminal.conf run[/blue]\n")
            return

        super().show_goodbye()
