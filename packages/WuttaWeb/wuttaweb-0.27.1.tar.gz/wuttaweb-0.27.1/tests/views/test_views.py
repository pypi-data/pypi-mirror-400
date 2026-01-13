# -*- coding: utf-8; -*-

import os
import sys
from unittest.mock import patch

from wuttaweb.testing import WebTestCase
from wuttaweb.views import views as mod
from wuttaweb.views.users import UserView


class TestMasterViewView(WebTestCase):

    def make_view(self):
        return mod.MasterViewView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.views")

    def test_get_grid_data(self):
        view = self.make_view()

        # empty by default, since nothing registered in test setup
        data = view.get_grid_data()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

        # so let's register one and try again
        self.pyramid_config.add_wutta_master_view(UserView)
        data = view.get_grid_data()
        self.assertGreater(len(data), 0)
        master = data[0]
        self.assertIsInstance(master, dict)
        self.assertEqual(master["model_title_plural"], "Users")
        self.assertEqual(master["model_name"], "User")
        self.assertEqual(master["url_prefix"], "/users")

    def test_configure_grid(self):
        self.pyramid_config.add_route("users", "/users/")
        self.pyramid_config.add_wutta_master_view(UserView)
        view = self.make_view()

        # sanity / coverage check
        grid = view.make_grid(
            columns=["model_title_plural", "url_prefix"], data=view.get_grid_data()
        )
        view.configure_grid(grid)

        # nb. must invoke this to exercise the url logic
        grid.get_vue_context()

    def test_get_template_context(self):
        view = self.make_view()
        with patch.object(view, "Session", return_value=self.session):

            # normal view gets no extra context
            context = view.get_template_context({})
            self.assertIsInstance(context, dict)
            self.assertNotIn("app_models", context)
            self.assertNotIn("view_module_dirs", context)
            self.assertNotIn("view_module_dir", context)
            self.assertNotIn("menu_path", context)
            self.assertNotIn("roles", context)
            self.assertNotIn("listing_roles", context)
            self.assertNotIn("creating_roles", context)
            self.assertNotIn("viewing_roles", context)
            self.assertNotIn("editing_roles", context)
            self.assertNotIn("deleting_roles", context)

            # but 'create' view gets extra context
            with patch.object(view, "creating", new=True):
                context = view.get_template_context({})
                self.assertIsInstance(context, dict)
                self.assertIn("app_models", context)
                self.assertIn("view_module_dirs", context)
                self.assertIn("view_module_dir", context)
                self.assertIn("menu_path", context)
                self.assertIn("roles", context)
                self.assertIn("listing_roles", context)
                self.assertIn("creating_roles", context)
                self.assertIn("viewing_roles", context)
                self.assertIn("editing_roles", context)
                self.assertIn("deleting_roles", context)

                # try that again but this time make sure there is only
                # one possibility for view module path, which is auto
                # selected by default
                with patch.object(
                    view, "get_view_module_options", return_value=["wuttaweb.views"]
                ):
                    context = view.get_template_context({})
                    self.assertEqual(context["view_module_dir"], "wuttaweb.views")

    def test_get_view_module_options(self):
        view = self.make_view()

        # register one master view, which should be reflected in options
        self.pyramid_config.add_wutta_master_view(UserView)
        options = view.get_view_module_options()
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0], "wuttaweb.views")

    def test_suggest_details(self):
        view = self.make_view()

        # first test uses model_class
        sample = {
            "action": "suggest_details",
            "model_option": "model_class",
            "model_name": "Person",
        }
        with patch.object(self.request, "json_body", new=sample, create=True):
            result = view.wizard_action()
            self.assertEqual(result["class_file_name"], "people.py")
            self.assertEqual(result["class_name"], "PersonView")
            self.assertEqual(result["model_name"], "Person")
            self.assertEqual(result["model_title"], "Person")
            self.assertEqual(result["model_title_plural"], "People")
            self.assertEqual(result["route_prefix"], "people")
            self.assertEqual(result["permission_prefix"], "people")
            self.assertEqual(result["url_prefix"], "/people")
            self.assertEqual(result["template_prefix"], "/people")
            self.assertIn("grid_columns", result)
            self.assertIsInstance(result["grid_columns"], str)
            self.assertIn("form_fields", result)
            self.assertIsInstance(result["form_fields"], str)

        # second test uses model_name
        sample = {
            "action": "suggest_details",
            "model_option": "model_name",
            "model_name": "acme_brick",
        }
        with patch.object(self.request, "json_body", new=sample, create=True):
            result = view.wizard_action()
            self.assertEqual(result["class_file_name"], "acme_bricks.py")
            self.assertEqual(result["class_name"], "AcmeBrickView")
            self.assertEqual(result["model_name"], "acme_brick")
            self.assertEqual(result["model_title"], "Acme Brick")
            self.assertEqual(result["model_title_plural"], "Acme Bricks")
            self.assertEqual(result["route_prefix"], "acme_bricks")
            self.assertEqual(result["permission_prefix"], "acme_bricks")
            self.assertEqual(result["url_prefix"], "/acme-bricks")
            self.assertEqual(result["template_prefix"], "/acme-bricks")
            self.assertEqual(result["grid_columns"], "")
            self.assertEqual(result["form_fields"], "")

    def test_write_view_file(self):
        view = self.make_view()
        view_file_path = self.write_file("silly_things.py", "")
        wutta_file_path = os.path.join(
            os.path.dirname(sys.modules["wuttaweb.views"].__file__),
            "silly_things.py",
        )
        self.assertEqual(os.path.getsize(view_file_path), 0)

        # first test w/ Upgrade model_class and target file path
        sample = {
            "action": "write_view_file",
            "view_location": None,
            "view_file_path": view_file_path,
            "overwrite": False,
            "class_name": "UpgradeView",
            "model_option": "model_class",
            "model_name": "Upgrade",
            "model_title": "Upgrade",
            "model_title_plural": "Upgrades",
            "route_prefix": "upgrades",
            "permission_prefix": "upgrades",
            "url_prefix": "/upgrades",
            "template_prefix": "/upgrades",
            "listable": True,
            "creatable": True,
            "viewable": True,
            "editable": True,
            "deletable": True,
            "grid_columns": ["description", "created_by"],
            "form_fields": ["description", "created_by"],
        }
        with patch.object(self.request, "json_body", new=sample, create=True):

            # does not overwrite by default
            result = view.wizard_action()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "File already exists")
            self.assertEqual(os.path.getsize(view_file_path), 0)

            # but can overwrite if requested
            with patch.dict(sample, {"overwrite": True}):
                result = view.wizard_action()
                self.assertNotIn("error", result)
                self.assertGreater(os.path.getsize(view_file_path), 1000)
                self.assertEqual(result["view_file_path"], view_file_path)
                self.assertEqual(
                    result["view_module_path"], "poser.web.views.silly_things"
                )

        # reset file
        with open(view_file_path, "wb") as f:
            pass
        self.assertEqual(os.path.getsize(view_file_path), 0)

        # second test w/ silly_thing model_name and target module path
        sample = {
            "action": "write_view_file",
            "view_location": "wuttaweb.views",
            "view_file_name": "silly_things.py",
            "overwrite": False,
            "class_name": "SillyThingView",
            "model_option": "model_name",
            "model_name": "silly_thing",
            "model_title": "Silly Thing",
            "model_title_plural": "Silly Things",
            "route_prefix": "silly_things",
            "permission_prefix": "silly_things",
            "url_prefix": "/silly-things",
            "template_prefix": "/silly-things",
            "listable": True,
            "creatable": True,
            "viewable": True,
            "editable": True,
            "deletable": True,
            "grid_columns": ["id", "name", "description"],
            "form_fields": ["id", "name", "description"],
        }
        with patch.object(self.request, "json_body", new=sample, create=True):

            # file does not yet exist, so will be written
            result = view.wizard_action()
            self.assertNotIn("error", result)
            self.assertEqual(result["view_file_path"], wutta_file_path)
            self.assertGreater(os.path.getsize(wutta_file_path), 1000)
            self.assertEqual(os.path.getsize(view_file_path), 0)
            self.assertEqual(result["view_module_path"], "wuttaweb.views.silly_things")

            # once file exists, will not overwrite by default
            result = view.wizard_action()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "File already exists")
            self.assertEqual(os.path.getsize(view_file_path), 0)

            # reset file
            with open(wutta_file_path, "wb") as f:
                pass
            self.assertEqual(os.path.getsize(wutta_file_path), 0)

            # can still overrwite explicitly
            with patch.dict(sample, {"overwrite": True}):
                result = view.wizard_action()
                self.assertNotIn("error", result)
                self.assertEqual(result["view_file_path"], wutta_file_path)
                self.assertGreater(os.path.getsize(wutta_file_path), 1000)
                self.assertEqual(os.path.getsize(view_file_path), 0)
                self.assertEqual(
                    result["view_module_path"], "wuttaweb.views.silly_things"
                )

            # nb. must be sure to deleta that file!
            os.remove(wutta_file_path)

    def test_check_route(self):
        self.pyramid_config.add_route("people", "/people/")
        view = self.make_view()
        sample = {
            "action": "check_route",
            "route": "people",
        }

        with patch.object(self.request, "json_body", new=sample, create=True):

            # should get url and path
            result = view.wizard_action()
            self.assertEqual(result["url"], "http://example.com/people/")
            self.assertEqual(result["path"], "/people/")
            self.assertNotIn("problem", result)

            # unless we check a bad route
            with patch.dict(sample, {"route": "invalid_nothing_burger"}):
                result = view.wizard_action()
            self.assertIn("problem", result)
            self.assertNotIn("url", result)
            self.assertNotIn("path", result)

    def test_apply_permissions(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(self.session)
        known = auth.get_role_authenticated(self.session)

        manager = model.Role(name="Manager")
        self.session.add(manager)

        worker = model.Role(name="worker")
        self.session.add(worker)

        fred = model.User(username="fred")
        fred.roles.append(manager)
        fred.roles.append(worker)
        self.session.add(fred)

        self.session.commit()

        self.assertFalse(auth.has_permission(self.session, fred, "people.list"))
        self.assertFalse(auth.has_permission(self.session, fred, "people.create"))
        self.assertFalse(auth.has_permission(self.session, fred, "people.view"))
        self.assertFalse(auth.has_permission(self.session, fred, "people.edit"))
        self.assertFalse(auth.has_permission(self.session, fred, "people.delete"))

        view = self.make_view()
        with patch.object(view, "Session", return_value=self.session):

            sample = {
                "action": "apply_permissions",
                "permission_prefix": "people",
                "listing_roles": {known.uuid.hex: True},
                "creating_roles": {worker.uuid.hex: True},
                "viewing_roles": {known.uuid.hex: True},
                "editing_roles": {manager.uuid.hex: True},
                "deleting_roles": {manager.uuid.hex: True},
            }
            with patch.object(self.request, "json_body", new=sample, create=True):

                # nb. empty result is normal
                result = view.wizard_action()
                self.assertEqual(result, {})

                self.assertTrue(auth.has_permission(self.session, fred, "people.list"))
                self.assertTrue(
                    auth.has_permission(self.session, fred, "people.create")
                )
                self.assertTrue(auth.has_permission(self.session, fred, "people.view"))
                self.assertTrue(auth.has_permission(self.session, fred, "people.edit"))
                self.assertTrue(
                    auth.has_permission(self.session, fred, "people.delete")
                )

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
            self.request, "json_body", create=True, new={"action": "check_route"}
        ):
            with patch.object(view, "check_route", side_effect=RuntimeError("whoa")):
                result = view.wizard_action()
                self.assertIn("error", result)
                self.assertEqual(result["error"], "Unexpected error occurred: whoa")

    def test_configure(self):
        self.pyramid_config.add_route("home", "/")
        self.pyramid_config.add_route("login", "/auth/login")
        self.pyramid_config.add_route("master_views", "/views/master")
        view = self.make_view()

        # sanity/coverage
        view.configure()
