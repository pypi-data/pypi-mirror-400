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
Table Views
"""

import os
import sys

from alembic import command as alembic_command
from sqlalchemy_utils import get_mapper
from mako.lookup import TemplateLookup
from webhelpers2.html import HTML

from wuttjamaican.db.conf import (
    check_alembic_current,
    make_alembic_config,
    get_alembic_scriptdir,
)

from wuttaweb.views import MasterView


class AppTableView(MasterView):  # pylint: disable=abstract-method
    """
    Master view showing all tables in the :term:`app database`.

    Default route prefix is ``app_tables``.

    Notable URLs provided by this class:

    * ``/tables/app/``
    * ``/tables/app/XXX``
    """

    # pylint: disable=duplicate-code
    model_name = "app_table"
    model_title = "App Table"
    model_key = "name"
    url_prefix = "/tables/app"
    filterable = False
    sortable = True
    sort_on_backend = False
    paginated = True
    paginate_on_backend = False
    creatable = True
    editable = False
    deletable = False
    # pylint: enable=duplicate-code

    labels = {
        "name": "Table Name",
        "module_name": "Module",
        "module_file": "File",
    }

    grid_columns = [
        "name",
        "schema",
        # "row_count",
    ]

    sort_defaults = "name"

    form_fields = [
        "name",
        "schema",
        "model_name",
        "description",
        # "row_count",
        "module_name",
        "module_file",
    ]

    has_rows = True
    rows_title = "Columns"
    rows_filterable = False
    rows_sort_defaults = "sequence"
    rows_sort_on_backend = False
    rows_paginated = True
    rows_paginate_on_backend = False
    rows_viewable = False

    row_grid_columns = [
        "sequence",
        "column_name",
        "data_type",
        "nullable",
        "description",
    ]

    def normalize_table(self, table):  # pylint: disable=missing-function-docstring
        record = {
            "name": table.name,
            "schema": table.schema or "",
            # "row_count": 42,
        }

        try:
            cls = get_mapper(table).class_
        except ValueError:
            pass
        else:
            record.update(
                {
                    "model_class": cls,
                    "model_name": cls.__name__,
                    "model_name_dotted": f"{cls.__module__}.{cls.__name__}",
                    "description": (cls.__doc__ or "").strip(),
                    "module_name": cls.__module__,
                    "module_file": sys.modules[cls.__module__].__file__,
                }
            )

        return record

    def get_grid_data(  # pylint: disable=empty-docstring
        self, columns=None, session=None
    ):
        """ """
        model = self.app.model
        data = []

        for table in model.Base.metadata.tables.values():
            data.append(self.normalize_table(table))

        return data

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # nb. show more tables by default
        g.pagesize = 50

        # schema
        g.set_searchable("schema")

        # name
        g.set_searchable("name")
        g.set_link("name")

    def get_instance(  # pylint: disable=empty-docstring,arguments-differ,unused-argument
        self, **kwargs
    ):
        """ """
        if "_cached_instance" not in self.__dict__:
            model = self.app.model

            name = self.request.matchdict["name"]
            table = model.Base.metadata.tables[name]

            # nb. sometimes need the real table reference later when
            # dealing with an instance view
            data = self.normalize_table(table)
            data["table"] = table

            self.__dict__["_cached_instance"] = data

        return self.__dict__["_cached_instance"]

    def get_instance_title(self, instance):  # pylint: disable=empty-docstring
        """ """
        return instance["name"]

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        # description
        f.set_widget("description", "notes")

    def get_xref_buttons(self, obj):
        """
        By default this returns a list of buttons for each
        :class:`~wuttaweb.views.master.MasterView` subclass registered
        in the app for the current table model.  Also a button to make
        a new Master View class, if permissions allow.

        See also parent method docs,
        :meth:`~wuttaweb.views.master.MasterView.get_xref_buttons()`
        """
        table = obj
        buttons = []

        # nb. we do not omit any buttons due to lack of permission
        # here.  all buttons are shown for anyone seeing this page.
        # this is for sake of clarity so admin users are aware of what
        # is *possible* within the app etc.
        master_views = self.request.registry.settings.get("wuttaweb_master_views", {})
        model_views = master_views.get(table["model_class"], [])
        for view in model_views:
            buttons.append(
                self.make_button(
                    view.get_model_title_plural(),
                    primary=True,
                    url=self.request.route_url(view.get_route_prefix()),
                    icon_left="eye",
                )
            )

        # only add "new master view" button if user has perm
        if self.request.has_perm("master_views.create"):
            # nb. separate slightly from others
            buttons.append(HTML.tag("br"))
            buttons.append(
                self.make_button(
                    "New Master View",
                    url=self.request.route_url("master_views.create"),
                    icon_left="plus",
                )
            )

        return buttons

    def get_row_grid_data(self, obj):  # pylint: disable=empty-docstring
        """ """
        table = obj
        data = []
        for i, column in enumerate(table["table"].columns, 1):
            data.append(
                {
                    "column": column,
                    "sequence": i,
                    "column_name": column.name,
                    "data_type": str(repr(column.type)),
                    "nullable": column.nullable,
                    "description": (column.doc or "").strip(),
                }
            )
        return data

    def configure_row_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_row_grid(g)

        # nb. try not to hide any columns by default
        g.pagesize = 100

        # sequence
        g.set_label("sequence", "Seq.")

        # column_name
        g.set_searchable("column_name")

        # data_type
        g.set_searchable("data_type")

        # nullable
        g.set_renderer("nullable", "boolean")

        # description
        g.set_searchable("description")
        g.set_renderer("description", self.render_column_description)

    def render_column_description(  # pylint: disable=missing-function-docstring,unused-argument
        self, column, field, value
    ):
        if not value:
            return ""

        max_length = 100
        if len(value) <= max_length:
            return value

        return HTML.tag("span", title=value, c=f"{value[:max_length]} ...")

    def get_template_context(self, context):  # pylint: disable=empty-docstring
        """ """
        if self.creating:
            model = self.app.model

            # alembic current
            context["alembic_is_current"] = check_alembic_current(self.config)

            # existing tables
            # TODO: any reason this should check grid data instead of metadata?
            unwanted = ["transaction", "transaction_meta"]
            context["existing_tables"] = [
                {"name": table}
                for table in sorted(model.Base.metadata.tables)
                if table not in unwanted and not table.endswith("_version")
            ]

            # model dir
            context["model_dir"] = os.path.dirname(model.__file__)

            # migration branch
            script = get_alembic_scriptdir(self.config)
            branch_options = self.get_migration_branch_options(script)
            context["migration_branch_options"] = branch_options
            branch = self.config.get(
                f"{self.config.appname}.alembic.default_revise_branch"
            )
            if not branch and len(branch_options) == 1:
                branch = branch_options[0]
            context["migration_branch"] = branch

        return context

    # TODO: this is effectivey duplicated in AlembicMigrationView.get_revise_branch_options()
    def get_migration_branch_options(  # pylint: disable=missing-function-docstring
        self, script
    ):
        branches = set()
        for rev in script.get_revisions(script.get_heads()):
            branches.update(rev.branch_labels)
        return sorted(branches)

    def wizard_action(self):  # pylint: disable=too-many-return-statements
        """
        AJAX view to handle various actions for the "new table" wizard.
        """
        data = self.request.json_body
        action = data.get("action", "").strip()
        try:

            # nb. cannot use match/case statement until python 3.10, but this
            # project technically still supports python 3.8
            if action == "write_model_file":
                return self.write_model_file(data)
            if action == "check_model":
                return self.check_model(data)
            if action == "write_revision_script":
                return self.write_revision_script(data)
            if action == "migrate_db":
                return self.migrate_db(data)
            if action == "check_table":
                return self.check_table(data)
            if action == "":
                return {"error": "Must specify the action to perform."}
            return {"error": f"Unknown action requested: {action}"}

        except Exception as err:  # pylint: disable=broad-exception-caught
            return {"error": f"Unexpected error occurred: {err}"}

    def write_model_file(self, data):  # pylint: disable=missing-function-docstring
        model = self.app.model
        path = data["module_file"]

        if os.path.exists(path):
            if data["overwrite"]:
                os.remove(path)
            else:
                return {"error": "File already exists"}

        for column in data["columns"]:
            if column["data_type"]["type"] == "_fk_uuid_" and column["relationship"]:
                name = column["relationship"]

                table = model.Base.metadata.tables[column["data_type"]["reference"]]
                mapper = get_mapper(table)
                reference_model = mapper.class_.__name__

                column["relationship"] = {
                    "name": name,
                    "reference_model": reference_model,
                }

        # TODO: make templates dir configurable?
        templates = [self.app.resource_path("wuttaweb:code-templates")]
        table_templates = TemplateLookup(directories=templates)

        template = table_templates.get_template("/new-table.mako")
        content = template.render(**data)
        with open(path, "wt", encoding="utf_8") as f:
            f.write(content)

        return {}

    def check_model(self, data):  # pylint: disable=missing-function-docstring
        model = self.app.model
        model_name = data["model_name"]

        if not hasattr(model, model_name):
            return {
                "problem": "class not found in app model",
                "model": model.__name__,
            }

        return {}

    def write_revision_script(self, data):  # pylint: disable=missing-function-docstring
        alembic_config = make_alembic_config(self.config)

        script = alembic_command.revision(
            alembic_config,
            autogenerate=True,
            head=f"{data['branch']}@head",
            message=data["message"],
        )

        return {"script": script.path}

    def migrate_db(  # pylint: disable=missing-function-docstring,unused-argument
        self, data
    ):
        alembic_config = make_alembic_config(self.config)
        alembic_command.upgrade(alembic_config, "heads")
        return {}

    def check_table(self, data):  # pylint: disable=missing-function-docstring
        model = self.app.model
        name = data["name"]

        table = model.Base.metadata.tables.get(name)
        if table is None:
            return {"problem": "table does not exist in app model"}

        session = self.Session()
        count = session.query(table).count()

        route_prefix = self.get_route_prefix()
        url = self.request.route_url(f"{route_prefix}.view", name=name)
        return {"url": url, "count": count}

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._apptable_defaults(config)
        cls._defaults(config)

    # pylint: disable=duplicate-code
    @classmethod
    def _apptable_defaults(cls, config):
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

    AppTableView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "AppTableView", base["AppTableView"]
    )
    AppTableView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
