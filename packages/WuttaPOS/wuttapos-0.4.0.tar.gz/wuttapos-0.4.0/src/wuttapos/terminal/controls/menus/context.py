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
WuttaPOS - "context" menu
"""

from .base import WuttaMenu


class WuttaContextMenu(WuttaMenu):

    def build_controls(self):
        # TODO: this should be empty by default, just giving
        # a couple of exmples until more functionality exists
        return [
            self.make_button_row(
                [
                    self.make_button(
                        "Refresh", bgcolor="blue", font_size=30, pos_cmd="refresh_txn"
                    ),
                    self.make_button(
                        "No-op", bgcolor="blue", font_size=30, pos_cmd="noop"
                    ),
                ]
            ),
        ]
