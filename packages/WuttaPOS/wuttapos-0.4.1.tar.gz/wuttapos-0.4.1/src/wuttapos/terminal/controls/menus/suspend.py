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
WuttaPOS - "suspend" menu
"""

from .base import WuttaMenu


class WuttaSuspendMenu(WuttaMenu):

    def build_controls(self):
        return [
            self.make_button_row(
                [
                    self.make_button(
                        "SUSPEND", bgcolor="purple", pos_cmd="suspend_txn"
                    ),
                    self.make_button("RESUME", bgcolor="purple", pos_cmd="resume_txn"),
                ]
            ),
            self.make_button_row(
                [
                    self.make_button(
                        "Cash",
                        bgcolor="orange",
                        pos_cmd="tender",
                        pos_cmd_kwargs={"tender": {"code": "CA"}},
                    ),
                    self.make_button(
                        "Check",
                        bgcolor="orange",
                        pos_cmd="tender",
                        pos_cmd_kwargs={"tender": {"code": "CK"}},
                    ),
                ]
            ),
            self.make_button_row(
                [
                    self.make_button(
                        "Food Stamps",
                        bgcolor="orange",
                        font_size=34,
                        pos_cmd="tender",
                        pos_cmd_kwargs={"tender": {"code": "FS"}},
                    ),
                ]
            ),
        ]
