# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Config Extension
"""

from wuttjamaican.conf import WuttaConfigExtension


class WuttaWebConfigExtension(WuttaConfigExtension):
    """
    Config extension for WuttaWeb.

    This sets the default plugin used for SQLAlchemy-Continuum, to
    :class:`~wuttaweb.db.continuum.WuttaWebContinuumPlugin`.  Which is
    only relevant if Wutta-Continuum is installed and enabled.  For
    more info see :doc:`wutta-continuum:index`.
    """

    key = "wuttaweb"

    def configure(self, config):  # pylint: disable=empty-docstring
        """ """
        config.setdefault(
            "wutta_continuum.wutta_plugin_spec",
            "wuttaweb.db.continuum:WuttaWebContinuumPlugin",
        )


def add_master_view(config, master):
    """
    Pyramid directive to add the given ``MasterView`` subclass to the
    app's registry.

    This allows the app to dynamically present certain options for
    admin features etc.

    This is normally called automatically for all master views, within
    the :meth:`~wuttaweb.views.master.MasterView.defaults()` method.

    Should you need to call this yourself, do not call it directly but
    instead make a similar call via the Pyramid config object::

       pyramid_config.add_wutta_master_view(PoserWidgetView)

    :param config: Reference to the Pyramid config object.

    :param master: Reference to a
       :class:`~wuttaweb.views.master.MasterView` subclass.

    This function is involved in app startup; once that phase is
    complete you can inspect the master views like so::

       master_views = request.registry.settings["wuttaweb_master_views"]

       # find master views for given model class
       user_views = master_views.get(model.User, [])

       # some master views are registered by model name instead (if no class)
       email_views = master_views.get("email_setting", [])
    """
    key = master.get_model_class() or master.get_model_name()

    def action():
        master_views = config.get_settings().get("wuttaweb_master_views", {})
        master_views.setdefault(key, []).append(master)
        config.add_settings({"wuttaweb_master_views": master_views})

    config.action(None, action)
