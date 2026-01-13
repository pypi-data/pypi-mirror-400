# -*- coding: utf-8; -*-

from wuttjamaican.db.model import User
from wuttjamaican.testing import ConfigTestCase

from wuttaweb import conf as mod
from wuttaweb.testing import WebTestCase
from wuttaweb.views import MasterView


class TestWuttaWebConfigExtension(ConfigTestCase):

    def test_basic(self):

        # continuum plugin not set yet (b/c config was not extended)
        self.assertIsNone(self.config.get("wutta_continuum.wutta_plugin_spec"))

        # so let's extend it
        extension = mod.WuttaWebConfigExtension()
        extension.configure(self.config)
        self.assertEqual(
            self.config.get("wutta_continuum.wutta_plugin_spec"),
            "wuttaweb.db.continuum:WuttaWebContinuumPlugin",
        )


class MasterWithClass(MasterView):
    model_class = User


class MasterWithName(MasterView):
    model_class = "Widget"


class TestAddMasterView(WebTestCase):

    def test_master_with_class(self):
        model = self.app.model

        # nb. due to minimal test bootstrapping, no master views are
        # registered by default at this point
        self.assertNotIn("wuttaweb_master_views", self.request.registry.settings)

        self.pyramid_config.add_wutta_master_view(MasterWithClass)
        self.assertIn("wuttaweb_master_views", self.request.registry.settings)
        master_views = self.request.registry.settings["wuttaweb_master_views"]
        self.assertIn(model.User, master_views)
        self.assertEqual(master_views[model.User], [MasterWithClass])

    def test_master_with_name(self):
        model = self.app.model

        # nb. due to minimal test bootstrapping, no master views are
        # registered by default at this point
        self.assertNotIn("wuttaweb_master_views", self.request.registry.settings)

        self.pyramid_config.add_wutta_master_view(MasterWithName)
        self.assertIn("wuttaweb_master_views", self.request.registry.settings)
        master_views = self.request.registry.settings["wuttaweb_master_views"]
        self.assertIn("Widget", master_views)
        self.assertEqual(master_views["Widget"], [MasterWithName])
