# -*- coding: utf-8; -*-

import os
from unittest.mock import patch

from alembic import command as alembic_command

from wuttjamaican.db.conf import check_alembic_current, make_alembic_config

from wuttaweb.testing import WebTestCase
from wuttaweb.views import tables as mod
from wuttaweb.views.users import UserView


class TestAppTableView(WebTestCase):

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
        return mod.AppTableView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.tables")

    def test_get_grid_data(self):
        view = self.make_view()
        data = view.get_grid_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        table = data[0]
        self.assertIsInstance(table, dict)
        self.assertIn("name", table)
        self.assertIn("schema", table)

    def test_configure_grid(self):
        view = self.make_view()

        # sanity / coverage check
        grid = view.make_grid(columns=["name", "schema"])
        view.configure_grid(grid)

    def test_get_instance(self):
        view = self.make_view()

        with patch.object(self.request, "matchdict", new={"name": "person"}):

            table1 = view.get_instance()
            self.assertIsInstance(table1, dict)
            self.assertIn("name", table1)
            self.assertEqual(table1["name"], "person")
            self.assertIn("schema", table1)

            table2 = view.get_instance()
            self.assertIs(table2, table1)
            self.assertEqual(table2["name"], "person")

    def test_get_instance_title(self):
        view = self.make_view()

        table = {"name": "poser_foo"}
        self.assertEqual(view.get_instance_title(table), "poser_foo")

    def test_configure_form(self):
        view = self.make_view()
        table = {"name": "user", "description": "Represents a user"}

        # no description widget by default
        form = view.make_form(model_instance=table, fields=["name", "description"])
        self.assertNotIn("description", form.widgets)

        # but it gets added when configuring
        view.configure_form(form)
        self.assertIn("description", form.widgets)

    def test_get_xref_buttons(self):
        self.pyramid_config.add_route("users", "/users/")
        self.pyramid_config.add_route("master_views.create", "/views/master/new")
        model = self.app.model
        view = self.make_view()

        # nb. must add this first
        self.pyramid_config.add_wutta_master_view(UserView)

        # should be just one xref button by default
        table = {"name": "user", "model_class": model.User}
        buttons = view.get_xref_buttons(table)
        self.assertEqual(len(buttons), 1)
        button = buttons[0]
        self.assertIn("Users", button)
        self.assertIn("http://example.com/users/", button)

        # unless we have perm to make new master view
        with patch.object(self.request, "is_root", new=True):
            table = {"name": "user", "model_class": model.User}
            buttons = view.get_xref_buttons(table)
            self.assertEqual(len(buttons), 3)
            first, second, third = buttons
            self.assertIn("Users", first)
            self.assertIn("http://example.com/users/", first)
            self.assertEqual(second, "<br />")
            self.assertIn("New Master View", third)
            self.assertIn("http://example.com/views/master/new", third)

    def test_get_row_grid_data(self):
        model = self.app.model
        view = self.make_view()

        table = model.Base.metadata.tables["person"]
        table_dict = {"name": "person", "table": table}

        data = view.get_row_grid_data(table_dict)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 4)
        columns = [c["column_name"] for c in data]
        self.assertIn("full_name", columns)
        self.assertIn("first_name", columns)
        self.assertIn("last_name", columns)

    def test_configure_row_grid(self):
        view = self.make_view()

        # sanity / coverage check
        grid = view.make_grid(columns=["column_name", "data_type"])
        view.configure_row_grid(grid)

    def test_render_column_description(self):
        view = self.make_view()

        # nb. first 2 params are igored
        text = view.render_column_description(None, None, "hello world")
        self.assertEqual(text, "hello world")

        text = view.render_column_description(None, None, "")
        self.assertEqual(text, "")
        text = view.render_column_description(None, None, None)
        self.assertEqual(text, "")

        msg = (
            "This is a very long and rambling sentence.  "
            "There is no point to it except that it is long.  "
            "Far too long to be reasonable."
            "I mean I am serious when I say this is simply too long."
        )
        text = view.render_column_description(None, None, msg)
        self.assertNotEqual(text, msg)
        self.assertIn("<span title=", text)

    def test_get_template_context(self):
        view = self.make_view()

        # normal view gets no extra context
        context = view.get_template_context({})
        self.assertIsInstance(context, dict)
        self.assertNotIn("alembic_is_current", context)
        self.assertNotIn("existing_tables", context)
        self.assertNotIn("model_dir", context)
        self.assertNotIn("migration_branch_options", context)
        self.assertNotIn("migration_branch", context)

        # but 'create' view gets extra context
        with patch.object(view, "creating", new=True):
            context = view.get_template_context({})
            self.assertIsInstance(context, dict)
            self.assertIn("alembic_is_current", context)
            self.assertIn("existing_tables", context)
            self.assertIn("model_dir", context)
            self.assertIn("migration_branch_options", context)
            self.assertIn("migration_branch", context)

    def test_write_model_file(self):
        view = self.make_view()
        module_path = self.write_file("widget.py", "")
        self.assertEqual(os.path.getsize(module_path), 0)

        sample = {
            "action": "write_model_file",
            "module_file": module_path,
            "overwrite": False,
            "table_name": "poser_widget",
            "model_name": "PoserWidget",
            "model_title": "Poser Widget",
            "model_title_plural": "Poser Widgets",
            "description": "A widget for Poser",
            "versioned": True,
            "columns": [
                {
                    "name": "uuid",
                    "data_type": {
                        "type": "UUID",
                    },
                    "formatted_data_type": "sa.UUID()",
                    "nullable": False,
                    "description": "primary key",
                    "versioned": "n/a",
                    "relationship": None,
                },
                {
                    "name": "name",
                    "data_type": {
                        "type": "String",
                    },
                    "formatted_data_type": "sa.String(length=100)",
                    "nullable": False,
                    "description": "name of widget",
                    "versioned": True,
                    "relationship": None,
                },
                {
                    "name": "owner_uuid",
                    "data_type": {
                        "type": "_fk_uuid_",
                        "reference": "user",
                    },
                    "formatted_data_type": "sa.UUID()",
                    "nullable": False,
                    "description": "owner of widget",
                    "versioned": True,
                    "relationship": {
                        "name": "owner",
                        "reference_model": "User",
                    },
                },
            ],
        }

        with patch.object(self.request, "json_body", new=sample, create=True):

            # does not overwrite by default
            result = view.wizard_action()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "File already exists")
            self.assertEqual(os.path.getsize(module_path), 0)

            # but it can overwrite if requested
            with patch.dict(sample, {"overwrite": True}):
                result = view.wizard_action()
                self.assertNotIn("error", result)
                self.assertGreater(os.path.getsize(module_path), 500)

    def test_check_model(self):
        view = self.make_view()
        sample = {
            "action": "check_model",
            "model_name": "Person",
        }

        with patch.object(self.request, "json_body", new=sample, create=True):

            # empty result means the model exists
            result = view.wizard_action()
            self.assertEqual(result, {})

            # problem is specified if not
            with patch.dict(sample, {"model_name": "gobbledygook"}):
                result = view.wizard_action()
                self.assertIn("problem", result)
                self.assertEqual(result["problem"], "class not found in app model")

    def test_write_revision_script(self):
        view = self.make_view()
        sample = {
            "action": "write_revision_script",
            "branch": "wutta",
            "message": "just a test",
        }

        # tell alembic our db is already current
        alembic = make_alembic_config(self.config)
        alembic_command.stamp(alembic, "heads")
        self.assertTrue(check_alembic_current(self.config, alembic))

        with patch.object(self.request, "json_body", new=sample, create=True):

            # nb. this writes a real script in the wuttjamaican project
            result = view.wizard_action()
            self.assertIn("script", result)
            outdir = os.path.dirname(result["script"])
            self.assertEqual(
                outdir, self.app.resource_path("wuttjamaican.db:alembic/versions")
            )

            # alembic now thinks we need to upgrade
            self.assertFalse(check_alembic_current(self.config, alembic))

            # must be sure to delete that script
            os.remove(result["script"])

    def test_migrate_db(self):
        view = self.make_view()
        sample = {"action": "migrate_db"}

        # tell alembic our db is already current
        alembic = make_alembic_config(self.config)
        alembic_command.stamp(alembic, "heads")
        self.assertTrue(check_alembic_current(self.config, alembic))

        # force downgrade to wutta@-1
        alembic_command.downgrade(alembic, "wutta@-1")

        # alembic now thinks we need to upgrade
        self.assertFalse(check_alembic_current(self.config, alembic))

        with patch.object(self.request, "json_body", new=sample, create=True):

            # now test our view method; alembic should then know we are current
            view.wizard_action()
            self.assertTrue(check_alembic_current(self.config, alembic))

    def test_check_table(self):
        self.pyramid_config.add_route("app_tables.view", "/tables/app/{name}")
        view = self.make_view()
        sample = {"action": "check_table", "name": "person"}

        with patch.object(view, "Session", return_value=self.session):

            with patch.object(self.request, "json_body", new=sample, create=True):

                # result with URL means the table exists
                result = view.wizard_action()
                self.assertIn("url", result)
                self.assertNotIn("problem", result)

                # problem is specified if not
                with patch.dict(sample, {"name": "gobbledygook"}):
                    result = view.wizard_action()
                self.assertIn("problem", result)
                self.assertEqual(result["problem"], "table does not exist in app model")

    def test_wizard_action(self):
        view = self.make_view()

        # missing action
        with patch.object(self.request, "json_body", create=True, new={}):
            result = view.wizard_action()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Must specify the action to perform.")

        # unknown action
        with patch.object(
            self.request, "json_body", create=True, new={"action": "nothing"}
        ):
            result = view.wizard_action()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Unknown action requested: nothing")

        # error invoking action
        with patch.object(
            self.request, "json_body", create=True, new={"action": "check_table"}
        ):
            with patch.object(view, "check_table", side_effect=RuntimeError("whoa")):
                result = view.wizard_action()
                self.assertIn("error", result)
                self.assertEqual(result["error"], "Unexpected error occurred: whoa")
