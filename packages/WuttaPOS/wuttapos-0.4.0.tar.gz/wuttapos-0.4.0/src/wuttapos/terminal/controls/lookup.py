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
WuttaPOS - base lookup control
"""

import flet as ft

from .keyboard import WuttaKeyboard
from wuttapos.terminal.controls.buttons import make_button


class WuttaLookup(ft.Container):

    default_font_size = 40
    font_size = default_font_size * 0.8
    default_button_height_dlg = 80
    disabled_bgcolor = "#aaaaaa"

    long_scroll_delta = 500

    def __init__(self, config, page=None, *args, **kwargs):
        self.on_reset = kwargs.pop("on_reset", None)
        self.show_search = kwargs.pop("show_search", True)
        self.initial_search = kwargs.pop("initial_search", None)
        self.allow_empty_query = kwargs.pop("allow_empty_query", False)
        self.on_select = kwargs.pop("on_select", None)
        self.on_cancel = kwargs.pop("on_cancel", None)

        super().__init__(*args, **kwargs)

        self.config = config
        self.app = config.get_app()
        self.enum = self.app.enum

        # TODO: this feels hacky
        self.mypage = page

        # track current selection
        self.selected_uuid = None
        self.selected_datarow = None

        self.search_results = ft.DataTable(
            columns=[
                ft.DataColumn(self.make_cell_text(text))
                for text in self.get_results_columns()
            ],
            data_row_min_height=50,
        )

        self.no_results = ft.Text(
            "NO RESULTS", size=32, color="red", weight=ft.FontWeight.BOLD, visible=False
        )

        self.select_button = make_button(
            "Select",
            font_size=self.font_size * 0.8,
            height=self.default_button_height_dlg * 0.8,
            width=self.default_button_height_dlg * 1.3,
            on_click=self.select_click,
            disabled=True,
            bgcolor=self.disabled_bgcolor,
        )

        self.up_button = make_button(
            "↑",
            font_size=self.font_size,
            height=self.default_button_height_dlg,
            width=self.default_button_height_dlg,
            on_click=self.up_click,
            on_long_press=self.up_longpress,
        )

        self.down_button = make_button(
            "↓",
            font_size=self.font_size,
            height=self.default_button_height_dlg,
            width=self.default_button_height_dlg,
            on_click=self.down_click,
            on_long_press=self.down_longpress,
        )

        self.search_results_wrapper = ft.Column(
            [
                self.search_results,
                self.no_results,
            ],
            expand=True,
            height=400,
            scroll=ft.ScrollMode.AUTO,
        )

        controls = []

        if self.show_search:

            self.searchbox = ft.TextField(
                "",
                text_size=self.font_size * 0.8,
                on_submit=self.lookup,
                autofocus=True,
                expand=True,
            )

            controls.extend(
                [
                    ft.Row(
                        [
                            ft.Text("SEARCH FOR:"),
                            self.searchbox,
                            make_button(
                                "Lookup",
                                font_size=self.font_size * 0.8,
                                height=self.default_button_height_dlg * 0.8,
                                width=self.default_button_height_dlg * 1.3,
                                on_click=self.lookup,
                                bgcolor="blue",
                            ),
                            make_button(
                                "Reset",
                                font_size=self.font_size * 0.8,
                                height=self.default_button_height_dlg * 0.8,
                                width=self.default_button_height_dlg * 1.3,
                                on_click=self.reset,
                                bgcolor="yellow",
                            ),
                        ],
                    ),
                    ft.Divider(),
                    WuttaKeyboard(
                        self.config,
                        on_keypress=self.keypress,
                        on_long_backspace=self.long_backspace,
                    ),
                ]
            )

        controls.extend(
            [
                ft.Divider(),
                ft.Row(
                    [
                        self.search_results_wrapper,
                        ft.VerticalDivider(),
                        ft.Column(
                            [
                                self.select_button,
                                ft.Row(),
                                ft.Row(),
                                ft.Row(),
                                ft.Row(),
                                ft.Row(),
                                self.up_button,
                                self.down_button,
                                ft.Row(),
                                ft.Row(),
                                ft.Row(),
                                ft.Row(),
                                ft.Row(),
                                make_button(
                                    "Cancel",
                                    font_size=self.font_size * 0.8,
                                    height=self.default_button_height_dlg * 0.8,
                                    width=self.default_button_height_dlg * 1.3,
                                    on_click=self.cancel,
                                ),
                            ],
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ]
        )

        self.content = ft.Column(controls=controls)
        self.height = None if self.show_search else 600

    def informed_refresh(self, **kwargs):
        pass

    def reset(self, e=None):
        if self.on_reset:
            self.on_reset(e=e)

    def get_results_columns(self):
        raise NotImplementedError

    def did_mount(self):
        if self.initial_search is not None:
            if self.show_search:
                self.searchbox.value = self.initial_search
            self.initial_search = None  # only do it once
            self.update()
            self.lookup()

    def make_cell_text(self, text):
        return ft.Text(text, size=32)

    def make_cell(self, text):
        return ft.DataCell(self.make_cell_text(text))

    def cancel(self, e):
        if self.on_cancel:
            self.on_cancel(e)

    def keypress(self, key):
        if key == "⏎":
            self.lookup()
        else:
            if key == "⌫":
                self.searchbox.value = self.searchbox.value[:-1]
            else:
                self.searchbox.value += key
            self.searchbox.focus()
            self.update()

    def long_backspace(self):
        self.searchbox.value = self.searchbox.value[:-10]
        self.searchbox.focus()
        self.update()

    def get_results(self, session, entry):
        raise NotImplementedError

    def make_result_row(self, obj):
        return obj

    def lookup(self, e=None):

        if self.show_search:
            entry = self.searchbox.value
            if not entry and not self.allow_empty_query:
                self.searchbox.focus()
                self.update()
                return
        else:
            entry = None

        session = self.app.make_session()
        results = self.get_results(session, entry)

        self.search_results.rows.clear()
        self.selected_uuid = None
        self.select_button.disabled = True
        self.select_button.bgcolor = self.disabled_bgcolor

        if results:
            for obj in results:
                self.search_results.rows.append(
                    ft.DataRow(
                        cells=[
                            self.make_cell(row) for row in self.make_result_row(obj)
                        ],
                        on_select_changed=self.select_changed,
                        data={"uuid": obj["uuid"]},
                    )
                )
            self.no_results.visible = False

        else:
            if self.show_search:
                self.no_results.value = f"NO RESULTS FOR: {entry}"
            else:
                self.no_results.value = "NO RESULTS FOUND"
            self.no_results.visible = True

        if self.show_search:
            self.searchbox.focus()
        self.update()

    def reset(self, e):
        if self.show_search:
            self.searchbox.value = ""
        self.search_results.rows.clear()
        self.no_results.visible = False
        self.selected_uuid = None
        self.selected_datarow = None
        self.select_button.disabled = True
        self.select_button.bgcolor = self.disabled_bgcolor
        if self.show_search:
            self.searchbox.focus()
        self.update()

    def set_selection(self, row):
        if self.selected_datarow:
            self.selected_datarow.color = None

        row.color = ft.colors.BLUE
        self.selected_uuid = row.data["uuid"]
        self.selected_datarow = row

        self.select_button.disabled = False
        self.select_button.bgcolor = "blue"

    def select_changed(self, e):
        if e.data:  # selected
            self.set_selection(e.control)
            self.update()

    def up_click(self, e):

        # select previous row, if selection in progress
        if self.selected_datarow:
            i = self.search_results.rows.index(self.selected_datarow)
            if i > 0:
                self.search_results_wrapper.scroll_to(delta=-48, duration=100)
                self.set_selection(self.search_results.rows[i - 1])
                self.update()
                return

        self.search_results_wrapper.scroll_to(delta=-50, duration=100)
        self.update()

    def up_longpress(self, e):
        self.search_results_wrapper.scroll_to(
            delta=-self.long_scroll_delta, duration=100
        )
        self.update()

    def down_click(self, e):

        # select next row, if selection in progress
        if self.selected_datarow:
            i = self.search_results.rows.index(self.selected_datarow)
            if (i + 1) < len(self.search_results.rows):
                self.search_results_wrapper.scroll_to(delta=48, duration=100)
                self.set_selection(self.search_results.rows[i + 1])
                self.update()
                return

        self.search_results_wrapper.scroll_to(delta=50, duration=100)
        self.update()

    def down_longpress(self, e):
        self.search_results_wrapper.scroll_to(
            delta=self.long_scroll_delta, duration=100
        )
        self.update()

    def select_click(self, e):
        if not self.selected_uuid:
            raise RuntimeError("no record selected?")
        if self.on_select:
            self.on_select(self.selected_uuid)
