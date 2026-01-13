# -*- coding: utf-8; -*-

import os
from unittest.mock import patch

import sqlalchemy as sa
from alembic import command as alembic_command

from wuttjamaican.testing import ConfigTestCase
from wuttjamaican.db.conf import (
    get_alembic_scriptdir,
    check_alembic_current,
    make_alembic_config,
)

import colander
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from wuttaweb.views import alembic as mod
from wuttaweb.forms import Form
from wuttaweb.testing import WebTestCase
from wuttaweb.forms.widgets import AlembicRevisionWidget


class TestNormalizeRevision(ConfigTestCase):

    def test_basic(self):
        self.config.setdefault("alembic.script_location", "wuttjamaican.db:alembic")
        self.config.setdefault(
            "alembic.version_locations", "wuttjamaican.db:alembic/versions"
        )

        script = get_alembic_scriptdir(self.config)
        head = script.get_heads()[0]
        rev = script.get_revision(head)

        result = mod.normalize_revision(self.config, rev)
        self.assertIsInstance(result, dict)
        self.assertIn("revision", result)
        self.assertEqual(result["revision"], rev.revision)


class TestAlembicMigrationView(WebTestCase):

    def setUp(self):
        super().setUp()
        self.config.setdefault("alembic.script_location", "wuttjamaican.db:alembic")
        self.config.setdefault(
            "alembic.version_locations", "wuttjamaican.db:alembic/versions"
        )

    def make_view(self):
        return mod.AlembicMigrationView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.alembic")

    def test_get_grid_data(self):
        view = self.make_view()
        data = view.get_grid_data()
        self.assertIsInstance(data, list)
        self.assertTrue(data)  # 1+ items
        rev = data[0]
        self.assertIn("revision", rev)
        self.assertIn("down_revision", rev)
        self.assertIn("doc", rev)

    def test_configure_grid(self):
        view = self.make_view()
        grid = view.make_model_grid()
        self.assertIn("revision", grid.searchable_columns)
        self.assertIn("doc", grid.searchable_columns)

    def test_render_is_head(self):
        view = self.make_view()

        # missing field / empty default
        rev = {"revision": "foo"}
        self.assertEqual(view.render_is_head(rev, "is_head", None), "")

        # boolean true
        rev = {"revision": "foo", "is_head": True}
        self.assertEqual(view.render_is_head(rev, "is_head", True), "Yes")

        # boolean false
        rev = {"revision": "foo", "is_head": False}
        self.assertEqual(view.render_is_head(rev, "is_head", False), "")

    def test_get_instance(self):
        view = self.make_view()

        with patch.object(self.request, "matchdict", new={"revision": "fc3a3bcaa069"}):

            rev1 = view.get_instance()
            self.assertIsInstance(rev1, dict)
            self.assertIn("revision", rev1)
            self.assertEqual(rev1["revision"], "fc3a3bcaa069")
            self.assertIn("doc", rev1)

            rev2 = view.get_instance()
            self.assertIs(rev2, rev1)
            self.assertEqual(rev2["revision"], "fc3a3bcaa069")

        view = self.make_view()
        with patch.object(self.request, "matchdict", new={"revision": "invalid"}):
            self.assertRaises(HTTPNotFound, view.get_instance)

    def test_get_instance_title(self):
        view = self.make_view()

        rev = {
            "revision": "fc3a3bcaa069",
            "doc": "init with settings table",
            "branch_labels": "wutta",
        }
        self.assertEqual(
            view.get_instance_title(rev), "(wutta) init with settings table"
        )

        rev = {
            "revision": "fc3a3bcaa069",
            "doc": "init with settings table",
            "branch_labels": "wutta",
            "is_head": True,
        }
        self.assertEqual(
            view.get_instance_title(rev), "(wutta) init with settings table [head]"
        )

    def test_configure_form(self):
        view = self.make_view()

        # sanity / coverage
        with patch.object(self.request, "matchdict", new={"revision": "fc3a3bcaa069"}):
            rev = view.get_instance()
            form = view.make_model_form(rev)
            self.assertIsInstance(form.widgets["down_revision"], AlembicRevisionWidget)

    def test_make_create_form(self):
        self.pyramid_config.add_route("alembic.migrations", "/alembic/migrations/")
        view = self.make_view()

        # sanity / coverage
        form = view.make_create_form()
        self.assertIsInstance(form, Form)
        self.assertIn("branching_option", form)

    def test_validate_revise_branch(self):
        self.pyramid_config.add_route("alembic.migrations", "/alembic/migrations/")
        view = self.make_view()
        form = view.make_create_form()
        schema = form.get_schema()

        # good example
        self.assertIsNone(
            view.validate_revise_branch(
                schema,
                {
                    "branching_option": "revise",
                    "revise_branch": "wutta",
                },
            )
        )

        # branch is required
        self.assertRaises(
            colander.Invalid,
            view.validate_revise_branch,
            schema,
            {
                "branching_option": "revise",
                "revise_branch": None,
            },
        )

    def test_validate_new_branch(self):
        self.pyramid_config.add_route("alembic.migrations", "/alembic/migrations/")
        view = self.make_view()
        form = view.make_create_form()
        schema = form.get_schema()

        # good example
        self.assertIsNone(
            view.validate_revise_branch(
                schema,
                {
                    "branching_option": "new",
                    "new_branch": "poser",
                    "version_location": "wuttjamaican.db:alembic/versions",
                },
            )
        )

        # name is required
        self.assertRaises(
            colander.Invalid,
            view.validate_new_branch,
            schema,
            {
                "branching_option": "new",
                "new_branch": None,
                "version_location": "wuttjamaican.db:alembic/versions",
            },
        )

        # version_location is required
        self.assertRaises(
            colander.Invalid,
            view.validate_new_branch,
            schema,
            {
                "branching_option": "new",
                "new_branch": "poser",
                "version_location": None,
            },
        )

    def test_save_create_form(self):
        self.pyramid_config.add_route("alembic.migrations", "/alembic/migrations/")
        self.pyramid_config.add_route("alembic.dashboard", "/alembic/dashboard")
        view = self.make_view()
        form = view.make_create_form()

        # revise branch
        form.validated = {
            "description": "test revision",
            "autogenerate": False,
            "branching_option": "revise",
            "revise_branch": "wutta",
        }
        revision = view.save_create_form(form)

        # file was saved in wutta dir
        self.assertTrue(
            revision.path.startswith(
                self.app.resource_path("wuttjamaican.db:alembic/versions")
            )
        )

        # get rid of that file!
        os.remove(revision.path)

        # new branch
        form.validated = {
            "description": "test revision",
            "autogenerate": False,
            "branching_option": "new",
            "new_branch": "wuttatest",
            "version_location": "wuttjamaican.db:alembic/versions",
        }
        revision = view.save_create_form(form)

        # file was saved in wutta dir
        self.assertTrue(
            revision.path.startswith(
                self.app.resource_path("wuttjamaican.db:alembic/versions")
            )
        )

        # get rid of that file!
        os.remove(revision.path)

    def test_save_delete_form(self):
        self.pyramid_config.add_route(
            "alembic.migrations.view", "/alembic/migrations/{revision}"
        )
        view = self.make_view()
        alembic = make_alembic_config(self.config)

        # write new empty migration script
        revision = alembic_command.revision(
            alembic,
            head="base",
            branch_label="wuttatest",
            version_path=self.app.resource_path("wuttjamaican.db:alembic/versions"),
            message="test revision",
        )

        # script exists
        self.assertTrue(os.path.exists(revision.path))

        with patch.object(
            self.request, "matchdict", new={"revision": revision.revision}
        ):
            form = view.make_delete_form(revision)
            view.save_delete_form(form)
            # script gone
            self.assertFalse(os.path.exists(revision.path))

    def test_configure(self):
        self.pyramid_config.add_route("home", "/")
        self.pyramid_config.add_route("login", "/auth/login")
        self.pyramid_config.add_route("alembic.migrations", "/alembic/migrations")
        view = self.make_view()

        # sanity/coverage
        view.configure()


class TestAlembicDashboardView(WebTestCase):

    def make_config(self, **kwargs):
        sqlite_path = self.write_file("test.sqlite", "")
        self.sqlite_engine_url = f"sqlite:///{sqlite_path}"

        config_path = self.write_file(
            "test.ini",
            f"""
[wutta.db]
default.url = {self.sqlite_engine_url}

[alembic]
script_location = wuttjamaican.db:alembic
version_locations = wuttjamaican.db:alembic/versions
""",
        )

        return super().make_config([config_path], **kwargs)

    def make_view(self):
        return mod.AlembicDashboardView(self.request)

    def test_dashboard(self):
        self.pyramid_config.add_route(
            "alembic.migrations.view", "/alembic/migrations/{revision}"
        )
        view = self.make_view()
        alembic = make_alembic_config(self.config)

        # tests use MetaData.create_all() instead of migrations for
        # setup, so alembic will assume db is not current
        self.assertFalse(check_alembic_current(self.config, alembic))

        # and to further prove the point, alembic_version table is missing
        self.assertEqual(
            self.session.execute(sa.text("select count(*) from person")).scalar(),
            0,
        )
        self.assertRaises(
            sa.exc.OperationalError,
            self.session.execute,
            sa.text("select count(*) from alembic_version"),
        )

        # therefore dashboard shows db with no heads at first
        context = view.dashboard()
        self.assertIsInstance(context, dict)
        self.assertIn("script_heads", context)
        self.assertEqual(len(context["script_heads"]), 1)
        self.assertIn("db_heads", context)
        self.assertEqual(len(context["db_heads"]), 0)

        # but we can 'stamp' the db as current
        alembic_command.stamp(alembic, "heads")

        # now the alembic_version table exists
        self.assertEqual(
            self.session.execute(
                sa.text("select count(*) from alembic_version")
            ).scalar(),
            1,
        )
        self.assertTrue(check_alembic_current(self.config, alembic))

        # and the dashboard knows about db heads
        context = view.dashboard()
        self.assertEqual(len(context["script_heads"]), 1)
        self.assertEqual(len(context["db_heads"]), 1)

    def test_migrate(self):
        self.pyramid_config.add_route("alembic.dashboard", "/alembic/dashboard")
        view = self.make_view()

        # tell alembic our db is already current
        alembic = make_alembic_config(self.config)
        alembic_command.stamp(alembic, "heads")
        self.assertTrue(check_alembic_current(self.config, alembic))

        # GET request redirects to dashboard w/ no flash
        result = view.migrate()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "http://example.com/alembic/dashboard")
        self.assertFalse(self.request.session.peek_flash())
        self.assertFalse(self.request.session.peek_flash("error"))

        # POST with no revspec also redirects but w/ flash
        with patch.object(self.request, "method", new="POST"):
            result = view.migrate()
            self.assertIsInstance(result, HTTPFound)
            self.assertEqual(result.location, "http://example.com/alembic/dashboard")
            self.assertFalse(self.request.session.peek_flash())
            self.assertTrue(self.request.session.peek_flash("error"))
            self.assertEqual(
                self.request.session.pop_flash("error"),
                ["You must provide a target revspec."],
            )

        # force downgrade to wutta@-1
        with patch.object(self.request, "method", new="POST"):
            with patch.object(
                self.request,
                "POST",
                new={"direction": "downgrade", "revspec": "wutta@-1"},
            ):
                # nb. this still redirects but w/ different flash
                result = view.migrate()
                self.assertIsInstance(result, HTTPFound)
                self.assertEqual(
                    result.location, "http://example.com/alembic/dashboard"
                )
                self.assertTrue(self.request.session.peek_flash())
                self.assertFalse(self.request.session.peek_flash("error"))
                self.assertEqual(
                    self.request.session.pop_flash(),
                    ["Database has been migrated."],
                )

        # alembic should know our db is no longer current
        self.assertFalse(check_alembic_current(self.config, alembic))

        # force upgrade to heads
        with patch.object(self.request, "method", new="POST"):
            with patch.object(
                self.request,
                "POST",
                new={"revspec": "heads"},
            ):
                # nb. this still redirects but w/ different flash
                result = view.migrate()
                self.assertIsInstance(result, HTTPFound)
                self.assertEqual(
                    result.location, "http://example.com/alembic/dashboard"
                )
                self.assertTrue(self.request.session.peek_flash())
                self.assertFalse(self.request.session.peek_flash("error"))
                self.assertEqual(
                    self.request.session.pop_flash(),
                    ["Database has been migrated."],
                )

        # alembic should know our db is current again
        self.assertTrue(check_alembic_current(self.config, alembic))

        # upgrade to invalid spec (force an error)
        with patch.object(self.request, "method", new="POST"):
            with patch.object(
                self.request,
                "POST",
                new={"revspec": "bad-spec"},
            ):
                # nb. this still redirects but w/ different flash
                result = view.migrate()
                self.assertIsInstance(result, HTTPFound)
                self.assertEqual(
                    result.location, "http://example.com/alembic/dashboard"
                )
                self.assertFalse(self.request.session.peek_flash())
                self.assertTrue(self.request.session.peek_flash("error"))
                [msg] = self.request.session.pop_flash("error")
                self.assertTrue(msg.startswith("Migrate failed: "))
