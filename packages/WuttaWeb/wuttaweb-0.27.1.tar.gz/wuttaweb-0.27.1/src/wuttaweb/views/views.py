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
Views of Views
"""

import importlib
import logging
import os
import re
import sys

from mako.lookup import TemplateLookup

from wuttaweb.views import MasterView
from wuttaweb.util import get_model_fields


log = logging.getLogger(__name__)


class MasterViewView(MasterView):  # pylint: disable=abstract-method
    """
    Master view which shows a list of all master views found in the
    app registry.

    Route prefix is ``master_views``; notable URLs provided by this
    class include:

    * ``/views/master/``
    """

    model_name = "master_view"
    model_title = "Master View"
    model_title_plural = "Master Views"
    url_prefix = "/views/master"

    filterable = False
    sortable = True
    sort_on_backend = False
    paginated = True
    paginate_on_backend = False

    creatable = True
    viewable = False  # nb. it has a pseudo-view action instead
    editable = False
    deletable = False
    configurable = True

    labels = {
        "model_title_plural": "Title",
        "url_prefix": "URL Prefix",
    }

    grid_columns = [
        "model_title_plural",
        "model_name",
        "route_prefix",
        "url_prefix",
    ]

    sort_defaults = "model_title_plural"

    def get_grid_data(  # pylint: disable=empty-docstring
        self, columns=None, session=None
    ):
        """ """
        data = []

        # nb. we do not omit any views due to lack of permission here.
        # all views are shown for anyone seeing this page.  this is
        # for sake of clarity so admin users are aware of what is
        # *possible* within the app etc.
        master_views = self.request.registry.settings.get("wuttaweb_master_views", {})
        for model_views in master_views.values():
            for view in model_views:
                data.append(
                    {
                        "model_title_plural": view.get_model_title_plural(),
                        "model_name": view.get_model_name(),
                        "route_prefix": view.get_route_prefix(),
                        "url_prefix": view.get_url_prefix(),
                    }
                )

        return data

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # nb. show more views by default
        g.pagesize = 50

        # nb. add "pseudo" View action
        def viewurl(view, i):  # pylint: disable=unused-argument
            return self.request.route_url(view["route_prefix"])

        g.add_action("view", icon="eye", url=viewurl)

        # model_title_plural
        g.set_link("model_title_plural")
        g.set_searchable("model_title_plural")

        # model_name
        g.set_searchable("model_name")

        # route_prefix
        g.set_searchable("route_prefix")

        # url_prefix
        g.set_link("url_prefix")
        g.set_searchable("url_prefix")

    def get_template_context(self, context):  # pylint: disable=empty-docstring
        """ """
        if self.creating:
            model = self.app.model
            session = self.Session()

            # app models
            app_models = []
            for name in dir(model):
                obj = getattr(model, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, model.Base)
                    and obj is not model.Base
                ):
                    app_models.append(name)
            context["app_models"] = sorted(app_models)

            # view module location
            view_locations = self.get_view_module_options()
            modpath = self.config.get("wuttaweb.master_views.default_module_dir")
            if modpath not in view_locations:
                modpath = None
            if not modpath and len(view_locations) == 1:
                modpath = view_locations[0]
            context["view_module_dirs"] = view_locations
            context["view_module_dir"] = modpath

            # menu handler path
            web = self.app.get_web_handler()
            menu = web.get_menu_handler()
            context["menu_path"] = sys.modules[menu.__class__.__module__].__file__

            # roles for access
            roles = self.get_roles_for_access(session)
            context["roles"] = [
                {"uuid": role.uuid.hex, "name": role.name} for role in roles
            ]
            context["listing_roles"] = {role.uuid.hex: False for role in roles}
            context["creating_roles"] = {role.uuid.hex: False for role in roles}
            context["viewing_roles"] = {role.uuid.hex: False for role in roles}
            context["editing_roles"] = {role.uuid.hex: False for role in roles}
            context["deleting_roles"] = {role.uuid.hex: False for role in roles}

        return context

    def get_roles_for_access(  # pylint: disable=missing-function-docstring
        self, session
    ):
        model = self.app.model
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(session)
        return (
            session.query(model.Role)
            .filter(model.Role.uuid != admin.uuid)
            .order_by(model.Role.name)
            .all()
        )

    def get_view_module_options(self):  # pylint: disable=missing-function-docstring
        modules = set()
        master_views = self.request.registry.settings.get("wuttaweb_master_views", {})
        for model_views in master_views.values():
            for view in model_views:
                parent = ".".join(view.__module__.split(".")[:-1])
                modules.add(parent)
        return sorted(modules)

    def wizard_action(self):  # pylint: disable=too-many-return-statements
        """
        AJAX view to handle various actions for the "new master view" wizard.
        """
        data = self.request.json_body
        action = data.get("action", "").strip()
        try:
            # nb. cannot use match/case statement until python 3.10, but this
            # project technically still supports python 3.8
            if action == "suggest_details":
                return self.suggest_details(data)
            if action == "write_view_file":
                return self.write_view_file(data)
            if action == "check_route":
                return self.check_route(data)
            if action == "apply_permissions":
                return self.apply_permissions(data)
            if action == "":
                return {"error": "Must specify the action to perform."}
            return {"error": f"Unknown action requested: {action}"}

        except Exception as err:  # pylint: disable=broad-exception-caught
            log.exception("new master view wizard action failed: %s", action)
            return {"error": f"Unexpected error occurred: {err}"}

    def suggest_details(  # pylint: disable=missing-function-docstring,too-many-locals
        self, data
    ):
        model = self.app.model
        model_name = data["model_name"]

        def make_normal(match):
            return "_" + match.group(1).lower()

        # normal is like:  poser_widget
        normal = re.sub(r"([A-Z])", make_normal, model_name)
        normal = normal.lstrip("_")

        def make_title(match):
            return " " + match.group(1).upper()

        # title is like:  Poser Widget
        title = re.sub(r"(?:^|_)([a-z])", make_title, normal)
        title = title.lstrip(" ")

        model_title = title
        model_title_plural = title + "s"

        def make_camel(match):
            return match.group(1).upper()

        # camel is like:  PoserWidget
        camel = re.sub(r"(?:^|_)([a-z])", make_camel, normal)

        # fields are unknown without model class
        grid_columns = []
        form_fields = []

        if data["model_option"] == "model_class":
            model_class = getattr(model, model_name)

            # get model title from model class, if possible
            if hasattr(model_class, "__wutta_hint__"):
                model_title = model_class.__wutta_hint__.get("model_title", model_title)
                model_title_plural = model_class.__wutta_hint__.get(
                    "model_title_plural", model_title + "s"
                )

            # get columns/fields from model class
            grid_columns = get_model_fields(self.config, model_class)
            form_fields = grid_columns

        # plural is like:  poser_widgets
        plural = re.sub(r"(?:^| )([A-Z])", make_normal, model_title_plural)
        plural = plural.lstrip("_")

        route_prefix = plural
        url_prefix = "/" + (plural).replace("_", "-")

        return {
            "class_file_name": plural + ".py",
            "class_name": camel + "View",
            "model_name": model_name,
            "model_title": model_title,
            "model_title_plural": model_title_plural,
            "route_prefix": route_prefix,
            "permission_prefix": route_prefix,
            "url_prefix": url_prefix,
            "template_prefix": url_prefix,
            "grid_columns": "\n".join(grid_columns),
            "form_fields": "\n".join(form_fields),
        }

    def write_view_file(self, data):  # pylint: disable=missing-function-docstring
        model = self.app.model

        # sort out the destination file path
        modpath = data["view_location"]
        if modpath:
            mod = importlib.import_module(modpath)
            file_path = os.path.join(
                os.path.dirname(mod.__file__), data["view_file_name"]
            )
        else:
            file_path = data["view_file_path"]

        # confirm file is writable
        if os.path.exists(file_path):
            if data["overwrite"]:
                os.remove(file_path)
            else:
                return {"error": "File already exists"}

        # guess its dotted module path
        modname, ext = os.path.splitext(  # pylint: disable=unused-variable
            os.path.basename(file_path)
        )
        if modpath:
            modpath = f"{modpath}.{modname}"
        else:
            modpath = f"poser.web.views.{modname}"

        # inject module for class if needed
        if data["model_option"] == "model_class":
            model_class = getattr(model, data["model_name"])
            data["model_module"] = model_class.__module__

        # TODO: make templates dir configurable?
        view_templates = TemplateLookup(
            directories=[self.app.resource_path("wuttaweb:code-templates")]
        )

        # render template to file
        template = view_templates.get_template("/new-master-view.mako")
        content = template.render(**data)
        with open(file_path, "wt", encoding="utf_8") as f:
            f.write(content)

        return {
            "view_file_path": file_path,
            "view_module_path": modpath,
            "view_config_path": os.path.join(os.path.dirname(file_path), "__init__.py"),
        }

    def check_route(self, data):  # pylint: disable=missing-function-docstring
        try:
            url = self.request.route_url(data["route"])
            path = self.request.route_path(data["route"])
        except Exception as err:  # pylint: disable=broad-exception-caught
            return {"problem": self.app.render_error(err)}

        return {"url": url, "path": path}

    def apply_permissions(  # pylint: disable=missing-function-docstring,too-many-branches
        self, data
    ):
        session = self.Session()
        auth = self.app.get_auth_handler()
        roles = self.get_roles_for_access(session)
        permission_prefix = data["permission_prefix"]

        if "listing_roles" in data:
            listing = data["listing_roles"]
            for role in roles:
                if listing.get(role.uuid.hex):
                    auth.grant_permission(role, f"{permission_prefix}.list")
                else:
                    auth.revoke_permission(role, f"{permission_prefix}.list")

        if "creating_roles" in data:
            creating = data["creating_roles"]
            for role in roles:
                if creating.get(role.uuid.hex):
                    auth.grant_permission(role, f"{permission_prefix}.create")
                else:
                    auth.revoke_permission(role, f"{permission_prefix}.create")

        if "viewing_roles" in data:
            viewing = data["viewing_roles"]
            for role in roles:
                if viewing.get(role.uuid.hex):
                    auth.grant_permission(role, f"{permission_prefix}.view")
                else:
                    auth.revoke_permission(role, f"{permission_prefix}.view")

        if "editing_roles" in data:
            editing = data["editing_roles"]
            for role in roles:
                if editing.get(role.uuid.hex):
                    auth.grant_permission(role, f"{permission_prefix}.edit")
                else:
                    auth.revoke_permission(role, f"{permission_prefix}.edit")

        if "deleting_roles" in data:
            deleting = data["deleting_roles"]
            for role in roles:
                if deleting.get(role.uuid.hex):
                    auth.grant_permission(role, f"{permission_prefix}.delete")
                else:
                    auth.revoke_permission(role, f"{permission_prefix}.delete")

        return {}

    def configure_get_simple_settings(self):  # pylint: disable=empty-docstring
        """ """
        return [
            {"name": "wuttaweb.master_views.default_module_dir"},
        ]

    def configure_get_context(  # pylint: disable=empty-docstring,arguments-differ
        self, **kwargs
    ):
        """ """
        context = super().configure_get_context(**kwargs)

        context["view_module_locations"] = self.get_view_module_options()

        return context

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._masterview_defaults(config)
        cls._defaults(config)

    # pylint: disable=duplicate-code
    @classmethod
    def _masterview_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()
        url_prefix = cls.get_url_prefix()

        # fix permission group
        config.add_wutta_permission_group(
            permission_prefix, model_title_plural, overwrite=False
        )

        # wizard actions
        config.add_route(
            f"{route_prefix}.wizard_action",
            f"{url_prefix}/new/wizard-action",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="wizard_action",
            route_name=f"{route_prefix}.wizard_action",
            renderer="json",
            permission=f"{permission_prefix}.create",
        )

    # pylint: enable=duplicate-code


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    MasterViewView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "MasterViewView", base["MasterViewView"]
    )
    MasterViewView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
