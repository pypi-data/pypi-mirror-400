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
WuttaPOS server web app
"""

from wuttaweb import app as base


def main(global_config, **settings):
    """
    Make and return the WSGI app (Paste entry point).
    """
    # prefer wuttapos templates over wuttaweb
    settings.setdefault(
        "mako.directories",
        [
            "wuttapos.server:templates",
            "wuttaweb:templates",
        ],
    )

    # make config objects
    wutta_config = base.make_wutta_config(settings)
    pyramid_config = base.make_pyramid_config(settings)

    # bring in the rest of wuttapos
    pyramid_config.include("wuttapos.server.static")
    pyramid_config.include("wuttapos.server.subscribers")
    pyramid_config.include("wuttapos.server.views")

    return pyramid_config.make_wsgi_app()


def make_wsgi_app():
    """
    Make and return the WSGI app (generic entry point).
    """
    return base.make_wsgi_app(main)


def make_asgi_app():
    """
    Make and return the ASGI app (generic entry point).
    """
    return base.make_asgi_app(main)
