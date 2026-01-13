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
Views for app settings
"""

import glob
import os
import logging

from wuttaweb.views import settings as base


log = logging.getLogger(__name__)


class AppInfoView(base.AppInfoView):
    """
    We override this view to add the :meth:`install_sample_data()` route.

    See also parent docs, :class:`~wuttaweb:wuttaweb.views.settings.AppInfoView`
    """

    def install_sample_data(self):
        """
        Special view to install sample data.  Probably just temporary until
        something better can be worked out...

        Requires root access; imports (create only) from small CSV
        files within the WuttaPOS code base.
        """

        # only root gets to do this
        if not self.request.is_root:
            raise self.forbidden()

        # we can't (yet?) tell the importer to import "everything"
        # because it will think that means "all models" as opposed to
        # "all files" found, and that raises error for missing files.
        # so we first inspect the folder to see what's there.
        models = []
        samples = self.app.resource_path("wuttapos:sample-data")
        # nb. should use root_dir param for glob() but requires python 3.10
        for path in glob.glob(os.path.join(samples, "*.csv")):
            name, ext = os.path.splitext(os.path.basename(path))
            models.append(name)

        # import all CSV files found in wuttapos/sample-data, but only
        # allow new records to be created, never update/delete
        try:
            handler = self.app.get_import_handler("import.to_wutta.from_csv")
            models = [name for name in models if name in handler.importers]
            kw = dict(input_file_path=samples, allow_update=False, allow_delete=False)
            handler.process_data(*models, **kw)
        except Exception as err:
            log.warning("failed to install sample data", exc_info=True)
            self.request.session.flash(
                f"Install failed: {self.app.render_error(err)}", "error"
            )
        else:
            self.request.session.flash("Sample data has been installed.")

        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._defaults(config)
        cls._appinfo_defaults(config)
        cls._wuttapos_defaults(config)

    @classmethod
    def _wuttapos_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()

        # install sample data
        config.add_route(
            f"{route_prefix}.install_sample_data",
            f"{url_prefix}/install-sample-data",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="install_sample_data",
            route_name=f"{route_prefix}.install_sample_data",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    local = globals()

    AppInfoView = kwargs.get("AppInfoView", local["AppInfoView"])

    base.defaults(config, **{"AppInfoView": AppInfoView})


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
