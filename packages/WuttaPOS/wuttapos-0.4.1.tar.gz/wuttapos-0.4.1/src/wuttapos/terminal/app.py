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
WuttaPOS app
"""

import logging
import socket
import sys
import threading
from collections import OrderedDict
from traceback import format_exception

from wuttjamaican.conf import make_config
from wuttjamaican.util import resource_path

import flet as ft

import wuttapos
from wuttapos.terminal.controls.buttons import make_button
from wuttapos.terminal.util import get_pos_batch_handler


log = logging.getLogger(__name__)


def main(page: ft.Page):
    config = make_config()
    app = config.get_app()
    model = app.model
    handler = get_pos_batch_handler(config)

    # nb. as of python 3.10 the original hook is accessible, we needn't save the ref
    # cf. https://docs.python.org/3/library/threading.html#threading.__excepthook__
    orig_thread_hook = threading.excepthook

    hostname = socket.gethostname()
    email_context = OrderedDict(
        [
            ("hostname", hostname),
            ("ipaddress", socket.gethostbyname(hostname)),
            ("terminal", handler.get_terminal_id() or "??"),
        ]
    )

    def handle_error(exc_type, exc_value, exc_traceback):

        log.exception("unhandled error in POS")

        # nb. ignore this particular error; it is benign
        if exc_type is RuntimeError and str(exc_value) == "Event loop is closed":
            log.debug("ignoring error for closed event loop", exc_info=True)
            return

        extra_context = OrderedDict(email_context)
        traceback = "".join(
            format_exception(exc_type, exc_value, exc_traceback)
        ).strip()

        try:
            uuid = page.session.get("user_uuid")
            if uuid:
                session = app.make_session()
                user = session.get(model.User, uuid)
                extra_context["username"] = user.username
                # TODO
                # batch = handler.get_current_batch(user, create=False)
                # if batch:
                #     extra_context['batchid'] = batch.id_str
                session.close()
            else:
                extra_context["username"] = "n/a"

            app.send_email(
                "uncaught_exception",
                {
                    "extra_context": extra_context,
                    "error": app.render_error(exc_value),
                    "traceback": traceback,
                },
            )

        except:
            log.exception("failed to send error email")

        try:

            def close_bs(e):
                bs.open = False
                bs.update()

            bs = ft.BottomSheet(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text(
                                "Unexpected Error", size=24, weight=ft.FontWeight.BOLD
                            ),
                            ft.Divider(),
                            ft.Text(
                                "Please be advised, something unexpected has gone wrong.\n"
                                "The state of your transaction may be questionable.\n\n"
                                "If possible you should consult the IT administrator.\n"
                                "(They may have already received an email about this.)",
                                size=20,
                            ),
                            ft.Container(
                                content=make_button(
                                    "Dismiss", on_click=close_bs, height=80, width=120
                                ),
                                alignment=ft.alignment.center,
                                expand=1,
                            ),
                        ],
                    ),
                    bgcolor="yellow",
                    padding=20,
                ),
                open=True,
                dismissible=False,
            )

            page.overlay.append(bs)
            page.update()

        except:
            log.exception("failed to show error bottomsheet")

    def sys_exc_hook(exc_type, exc_value, exc_traceback):
        handle_error(exc_type, exc_value, exc_traceback)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def thread_exc_hook(args):
        handle_error(args.exc_type, args.exc_value, args.exc_traceback)
        # nb. as of python 3.10 could just call threading.__excepthook__ instead
        # cf. https://docs.python.org/3/library/threading.html#threading.__excepthook__
        orig_thread_hook(args)

    # custom exception hook for main process
    sys.excepthook = sys_exc_hook

    # custom exception hook for threads (requires python 3.8)
    # cf. https://docs.python.org/3/library/threading.html#threading.excepthook
    v = sys.version_info
    if v.major >= 3 and v.minor >= 8:
        threading.excepthook = thread_exc_hook

    page.title = f"WuttaPOS v{wuttapos.__version__}"
    if hasattr(page, "window"):
        page.window.full_screen = True
    else:
        page.window_full_screen = True

    # global defaults for button/text styles etc.
    page.data = {
        "default_button_height_pos": 100,
        "default_button_height_dlg": 80,
    }

    def clean_exit():
        # TODO: this doesn't do anything interesting now, but it could
        if hasattr(page, "window"):
            page.window.destroy()
        else:
            page.window_destroy()

    def keyboard(e):
        # exit on ctrl+Q
        if e.ctrl and e.key == "Q":
            if not e.shift and not e.alt and not e.meta:
                clean_exit()

    page.on_keyboard_event = keyboard

    def window_event(e):
        if e.data == "close":
            clean_exit()

    # cf. https://flet.dev/docs/controls/page/#window_destroy
    if hasattr(page, "window"):
        page.window.prevent_close = True
        page.window.on_event = window_event
    else:
        page.window_prevent_close = True
        page.window_on_event = window_event

    # TODO: probably these should be auto-loaded from spec
    from wuttapos.terminal.views.pos import POSView
    from wuttapos.terminal.views.login import LoginView

    # cf .https://flet.dev/docs/guides/python/navigation-and-routing#building-views-on-route-change

    def route_change(e):
        page.views.clear()

        redirect = None
        user_uuid = page.session.get("user_uuid")
        if page.route == "/login" and user_uuid:
            redirect = "/pos"
            other = "/pos"
        elif page.route == "/pos" and not user_uuid:
            redirect = "/login"
            other = "/login"
        else:
            redirect = "/pos" if user_uuid else "/login"

        if redirect and page.route != redirect:
            page.go(redirect)
            return

        if page.route == "/pos":
            page.views.append(POSView(config, "/pos"))

        elif page.route == "/login":
            page.views.append(LoginView(config, "/login"))

        if hasattr(page, "window"):
            page.window.full_screen = True
        else:
            page.window_full_screen = True

        page.update()

    # TODO: this was in example docs but not sure what it's for?
    # def view_pop(view):
    #     page.views.pop()
    #     top_view = page.views[-1]
    #     page.go(top_view.route)

    page.on_route_change = route_change
    # page.on_view_pop = view_pop

    # TODO: this may be too hacky but is useful for now/dev
    if not config.production():

        training = page.client_storage.get("training")
        page.session.set("training", training)

        user = None
        uuid = page.client_storage.get("user_uuid")
        if uuid:
            session = app.make_session()
            user = session.get(model.User, uuid)
            if user:
                page.session.set("user_uuid", user.uuid.hex)
                page.session.set("user_display", str(user))

                if batch := handler.get_current_batch(user, create=False):
                    page.session.set("txn_display", batch.id_str)
                    if batch.customer:
                        page.session.set("cust_uuid", batch.customer.uuid)
                        page.session.set(
                            "cust_display", handler.get_screen_cust_display(txn=txn)
                        )

                session.close()
                page.go("/pos")
                return

            session.close()

    page.go("/login")


# TODO: is there any way to inject a config object into the new Flet
# app?  if so this would be the place to do it.  currently in main()
# it always makes a new config for itself, as workaround.  but also
# see notes in the wuttapos.cli.run module
def run_app():
    ft.app(target=main, assets_dir=resource_path("wuttapos.terminal:assets"))


if __name__ == "__main__":
    run_app()
