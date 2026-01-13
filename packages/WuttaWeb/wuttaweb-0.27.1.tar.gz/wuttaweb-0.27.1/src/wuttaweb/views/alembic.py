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
Views for Alembic
"""

import datetime
import logging
import os
import re

from alembic import command as alembic_command
from alembic.migration import MigrationContext
from alembic.util import CommandError

from wuttjamaican.db.conf import (
    make_alembic_config,
    get_alembic_scriptdir,
    check_alembic_current,
)

import colander
from webhelpers2.html import tags, HTML

from wuttaweb.views import View, MasterView
from wuttaweb.forms import widgets


log = logging.getLogger(__name__)


def normalize_revision(config, rev):  # pylint: disable=missing-function-docstring
    app = config.get_app()

    created = None
    if match := re.search(r"Create Date: (\d{4}-\d{2}-\d{2}[\d:\. ]+\d)", rev.longdoc):
        created = datetime.datetime.fromisoformat(match.group(1))
        created = app.localtime(created, from_utc=False)
        created = app.render_datetime(created)

    return {
        "revision": rev.revision,
        "branch_labels": ", ".join(rev.branch_labels),
        "doc": rev.doc,
        "longdoc": rev.longdoc,
        "path": rev.path,
        "dependencies": rev.dependencies or "",
        "down_revision": rev.down_revision or "",
        "nextrev": ", ".join(rev.nextrev),
        "is_base": app.render_boolean(rev.is_base),
        "is_branch_point": app.render_boolean(rev.is_branch_point),
        "is_head": rev.is_head,
        "created": created,
    }


class AlembicDashboardView(View):
    """
    Custom views for the Alembic Dashboard.
    """

    def dashboard(self):
        """
        Main view for the Alembic Dashboard.

        Route name is ``alembic.dashboard``; URL is
        ``/alembic/dashboard``
        """
        script = get_alembic_scriptdir(self.config)
        with self.config.appdb_engine.begin() as conn:
            context = MigrationContext.configure(conn)
            current_heads = context.get_current_heads()

        def normalize(rev):
            normal = normalize_revision(self.config, rev)
            normal["is_current"] = rev.revision in current_heads

            normal["revision"] = tags.link_to(
                normal["revision"],
                self.request.route_url(
                    "alembic.migrations.view", revision=normal["revision"]
                ),
            )

            if normal["down_revision"]:
                normal["down_revision"] = tags.link_to(
                    normal["down_revision"],
                    self.request.route_url(
                        "alembic.migrations.view", revision=normal["down_revision"]
                    ),
                )

            return normal

        script_heads = []
        for head in script.get_heads():
            rev = script.get_revision(head)
            script_heads.append(normalize(rev))

        db_heads = []
        for head in current_heads:
            rev = script.get_revision(head)
            db_heads.append(normalize(rev))

        script_heads.sort(key=lambda rev: rev["branch_labels"])
        db_heads.sort(key=lambda rev: rev["branch_labels"])

        return {
            "index_title": "Alembic Dashboard",
            "script": {
                "dir": script.dir,
                "version_locations": sorted(script.version_locations),
                "env_py_location": script.env_py_location,
                "file_template": script.file_template,
            },
            "script_heads": script_heads,
            "db_heads": db_heads,
        }

    def migrate(self):
        """
        Action view to migrate the database.  POST request must be used.

        This directly invokes the :func:`alembic upgrade
        <alembic:alembic.command.upgrade>` (or :func:`alembic
        downgrade <alembic:alembic.command.downgrade>`) command.

        It then sets a flash message per the command status, and
        redirects user back to the Dashboard (or other referrer).

        The request must specify a ``revspec`` param, which we pass
        along as-is to the ``alembic`` command.  We assume ``alembic
        upgrade`` unless the request sets ``direction`` param to
        ``"downgrade"``.
        """
        referrer = self.request.get_referrer(
            default=self.request.route_url("alembic.dashboard")
        )
        if self.request.method != "POST":
            return self.redirect(referrer)

        revspec = self.request.POST.get("revspec")
        if not revspec:
            self.request.session.flash("You must provide a target revspec.", "error")

        else:
            direction = self.request.POST.get("direction")
            if direction != "downgrade":
                direction = "upgrade"
            alembic = make_alembic_config(self.config)
            command = (
                alembic_command.downgrade
                if direction == "downgrade"
                else alembic_command.upgrade
            )

            # invoke alembic upgrade/downgrade
            try:
                command(alembic, revspec)
            except Exception as err:  # pylint: disable=broad-exception-caught
                log.exception(
                    "database failed to %s using revspec: %s", direction, revspec
                )
                self.request.session.flash(f"Migrate failed: {err}", "error")
            else:
                self.request.session.flash("Database has been migrated.")

        return self.redirect(referrer)

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):

        # permission group
        config.add_wutta_permission_group(
            "alembic", "Alembic (General)", overwrite=False
        )

        # dashboard
        config.add_wutta_permission(
            "alembic",
            "alembic.dashboard",
            "Basic (view) access to the Alembic Dashboard",
        )
        config.add_route("alembic.dashboard", "/alembic/dashboard")
        config.add_view(
            cls,
            attr="dashboard",
            route_name="alembic.dashboard",
            renderer="/alembic/dashboard.mako",
            permission="alembic.dashboard",
        )

        # migrate
        config.add_wutta_permission(
            "alembic",
            "alembic.migrate",
            "Run migration scripts on the database",
        )
        config.add_route("alembic.migrate", "/alembic/migrate")
        config.add_view(
            cls,
            attr="migrate",
            route_name="alembic.migrate",
            permission="alembic.migrate",
        )


class AlembicMigrationView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for Alembic Migrations.

    Route prefix is ``alembic.migrations``; notable URLs include:

    * ``/alembic/migrations/``
    * ``/alembic/migrations/new``
    * ``/alembic/migrations/XXX``
    """

    # pylint: disable=duplicate-code
    model_name = "alembic_migration"
    model_key = "revision"
    model_title = "Alembic Migration"
    route_prefix = "alembic.migrations"
    url_prefix = "/alembic/migrations"
    filterable = False
    sortable = True
    sort_on_backend = False
    paginated = True
    paginate_on_backend = False
    editable = False
    configurable = True
    # pylint: enable=duplicate-code

    labels = {
        "doc": "Description",
        "longdoc": "Long Description",
        "nextrev": "Next Revision",
    }

    grid_columns = [
        "is_head",
        "revision",
        "doc",
        "branch_labels",
        "down_revision",
        "created",
    ]

    sort_defaults = ("is_head", "desc")

    form_fields = [
        "revision",
        "doc",
        "longdoc",
        "branch_labels",
        "dependencies",
        "down_revision",
        "nextrev",
        "is_base",
        "is_branch_point",
        "is_head",
        "path",
        "created",
    ]

    def get_grid_data(  # pylint: disable=empty-docstring
        self, columns=None, session=None
    ):
        """ """
        data = []
        script = get_alembic_scriptdir(self.config)
        for rev in script.walk_revisions():
            data.append(normalize_revision(self.config, rev))
        return data

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # revision
        g.set_link("revision")
        g.set_searchable("revision")

        # doc
        g.set_link("doc")
        g.set_searchable("doc")

        # branch_labels
        g.set_searchable("branch_labels")

        # is_head
        g.set_label("is_head", "Head")
        g.set_renderer("is_head", self.render_is_head)

    def render_is_head(  # pylint: disable=missing-function-docstring,unused-argument
        self, rev, field, value
    ):
        return self.app.render_boolean(value) if value else ""

    def get_instance(
        self, **kwargs
    ):  # pylint: disable=empty-docstring,arguments-differ,unused-argument
        """ """
        if "_cached_instance" not in self.__dict__:
            revision = self.request.matchdict["revision"]
            script = get_alembic_scriptdir(self.config)
            try:
                rev = script.get_revision(revision)
            except CommandError:
                rev = None
            if not rev:
                raise self.notfound()
            self.__dict__["_cached_instance"] = normalize_revision(self.config, rev)
        return self.__dict__["_cached_instance"]

    def get_instance_title(self, instance):  # pylint: disable=empty-docstring
        """ """
        text = f"({instance['branch_labels']}) {instance['doc']}"
        if instance.get("is_head"):
            text += " [head]"
        return text

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        # revision
        f.set_widget("revision", widgets.CopyableTextWidget())

        # longdoc
        f.set_widget("longdoc", "notes")

        # down_revision
        f.set_widget("down_revision", widgets.AlembicRevisionWidget(self.request))

        # nextrev
        f.set_widget("nextrev", widgets.AlembicRevisionsWidget(self.request))

        # is_head
        f.set_node("is_head", colander.Boolean())

        # path
        f.set_widget("path", widgets.CopyableTextWidget())

    def make_create_form(self):  # pylint: disable=empty-docstring
        """ """
        alembic = make_alembic_config(self.config)
        script = get_alembic_scriptdir(self.config, alembic)

        schema = colander.Schema()
        schema.add(colander.SchemaNode(colander.String(), name="description"))

        schema.add(
            colander.SchemaNode(
                colander.Boolean(),
                name="autogenerate",
                default=check_alembic_current(self.config, alembic),
            )
        )

        schema.add(
            colander.SchemaNode(
                colander.String(), name="branching_option", default="revise"
            )
        )

        branch_options = self.get_revise_branch_options(script)

        revise_branch = colander.SchemaNode(
            colander.String(),
            name="revise_branch",
            missing=colander.null,
            validator=colander.OneOf(branch_options),
            widget=widgets.SelectWidget(values=[(b, b) for b in branch_options]),
        )

        branch = self.config.get(f"{self.config.appname}.alembic.default_revise_branch")
        if not branch and len(branch_options) == 1:
            branch = branch_options[0]
        if branch:
            revise_branch.default = branch

        schema.add(revise_branch)

        schema.add(
            colander.SchemaNode(
                colander.String(), name="new_branch", missing=colander.null
            )
        )

        version_locations = sorted(
            self.config.parse_list(alembic.get_main_option("version_locations"))
        )

        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="version_location",
                missing=colander.null,
                validator=colander.OneOf(version_locations),
                widget=widgets.SelectWidget(values=[(v, v) for v in version_locations]),
            )
        )

        schema.validator = colander.All(
            self.validate_revise_branch, self.validate_new_branch
        )

        form = self.make_form(
            schema=schema,
            cancel_url_fallback=self.get_index_url(),
            button_label_submit="Write Script File",
        )

        form.set_label("revise_branch", "Branch")

        return form

    def validate_revise_branch(  # pylint: disable=missing-function-docstring
        self, node, value
    ):
        if value["branching_option"] == "revise":
            if not value["revise_branch"]:
                node["revise_branch"].raise_invalid(
                    "Must specify which branch to revise."
                )

    def validate_new_branch(  # pylint: disable=missing-function-docstring
        self, node, value
    ):
        if value["branching_option"] == "new":

            if not value["new_branch"]:
                node["new_branch"].raise_invalid("New branch requires a name.")

            if not value["version_location"]:
                node["version_location"].raise_invalid(
                    "New branch requires a version location."
                )

    def save_create_form(self, form):  # pylint: disable=empty-docstring
        """ """
        alembic = make_alembic_config(self.config)
        data = form.validated

        # kwargs for `alembic revision` command
        kw = {
            "message": data["description"],
            "autogenerate": data["autogenerate"],
        }
        if data["branching_option"] == "new":
            kw["head"] = "base"
            kw["branch_label"] = data["new_branch"]
            kw["version_path"] = self.app.resource_path(data["version_location"])
        else:
            assert data["branching_option"] == "revise"
            kw["head"] = f"{data['revise_branch']}@head"

        # run `alembic revision`
        revision = alembic_command.revision(alembic, **kw)

        intro = HTML.tag(
            "p",
            class_="block",
            c="New migration script has been created.  "
            "Please review and modify the file contents as needed:",
        )

        path = HTML.tag(
            "p",
            class_="block has-background-white has-text-black is-family-monospace",
            style="padding: 0.5rem;",
            c=[HTML.tag("wutta-copyable-text", text=revision.path)],
        )

        outro = HTML.tag(
            "p",
            class_="block",
            c=[
                "When satisfied, proceed to ",
                tags.link_to(
                    "Migrate Database", self.request.route_url("alembic.dashboard")
                ),
                ".",
            ],
        )

        self.request.session.flash(HTML.tag("div", c=[intro, path, outro]))
        return revision

    def save_delete_form(self, form):  # pylint: disable=empty-docstring
        """ """
        rev = self.get_instance()
        os.remove(rev["path"])

    # TODO: this is effectivey duplicated in AppTableView.get_migration_branch_options()
    def get_revise_branch_options(  # pylint: disable=missing-function-docstring
        self, script
    ):
        branches = set()
        for rev in script.get_revisions(script.get_heads()):
            branches.update(rev.branch_labels)
        return sorted(branches)

    def configure_get_simple_settings(self):  # pylint: disable=empty-docstring
        """ """
        return [
            {"name": f"{self.config.appname}.alembic.default_revise_branch"},
        ]

    def configure_get_context(  # pylint: disable=empty-docstring,arguments-differ
        self, **kwargs
    ):
        """ """
        context = super().configure_get_context(**kwargs)

        script = get_alembic_scriptdir(self.config)
        context["revise_branch_options"] = self.get_revise_branch_options(script)

        return context


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    AlembicDashboardView = (  # pylint: disable=invalid-name,redefined-outer-name
        kwargs.get("AlembicDashboardView", base["AlembicDashboardView"])
    )
    AlembicDashboardView.defaults(config)

    AlembicMigrationView = (  # pylint: disable=invalid-name,redefined-outer-name
        kwargs.get("AlembicMigrationView", base["AlembicMigrationView"])
    )
    AlembicMigrationView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
