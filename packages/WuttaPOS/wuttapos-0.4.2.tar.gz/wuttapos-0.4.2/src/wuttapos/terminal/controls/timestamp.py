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
WuttaPOS - timestamp control
"""

import asyncio
import datetime
import threading
import time

import flet as ft


class WuttaTimestamp(ft.Text):

    def __init__(self, config, page=None, *args, **kwargs):
        self.on_reset = kwargs.pop("on_reset", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = self.config.get_app()

        self.value = self.render_time(datetime.datetime.now())

    def did_mount(self):
        self.running = True
        if hasattr(self.page, "run_task"):
            self.page.run_task(self.update_display)
        else:
            # nb. daemonized thread should be stopped when app exits
            # cf. https://docs.python.org/3/library/threading.html#thread-objects
            thread = threading.Thread(target=self.update_display_blocking, daemon=True)
            thread.start()

    def will_unmount(self):
        self.running = False

    def render_time(self, value):
        return value.strftime("%a %d %b %Y - %I:%M:%S %p")

    async def update_display(self):
        while self.running:
            self.value = self.render_time(datetime.datetime.now())
            self.update()
            await asyncio.sleep(0.5)

    def update_display_blocking(self):
        while self.running:
            # self.value = self.render_time(self.app.localtime())
            self.value = self.render_time(datetime.datetime.now())
            self.update()
            time.sleep(0.5)
