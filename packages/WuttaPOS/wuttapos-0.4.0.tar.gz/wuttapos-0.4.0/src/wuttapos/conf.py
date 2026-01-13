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
WuttaPOS config extension
"""

from wuttjamaican.conf import WuttaConfigExtension


class WuttaPosConfigExtension(WuttaConfigExtension):
    """
    The :term`config extension` for WuttaPOS.
    """

    key = "wuttapos"

    def configure(self, config):

        # app info
        config.setdefault(f"{config.appname}.app_title", "WuttaPOS")
        config.setdefault(f"{config.appname}.app_dist", "WuttaPOS")

        # app handler
        config.setdefault(
            f"{config.appname}.app.handler", "wuttapos.app:WuttaPosAppHandler"
        )

        # app model
        config.setdefault(f"{config.appname}.model_spec", "wuttapos.db.model")
        config.setdefault(f"{config.appname}.enum_spec", "wuttapos.enum")

        # # auth handler
        # config.setdefault(
        #     f"{config.appname}.auth.handler", "wuttapos.auth:WuttaPosAuthHandler"
        # )

        # server menu handler
        config.setdefault(
            f"{config.appname}.web.menus.handler.spec",
            "wuttapos.server.menus:WuttaPosMenuHandler",
        )

        # # web app libcache
        # #config.setdefault('wuttaweb.static_libcache.module', 'wuttapos.server.static')
