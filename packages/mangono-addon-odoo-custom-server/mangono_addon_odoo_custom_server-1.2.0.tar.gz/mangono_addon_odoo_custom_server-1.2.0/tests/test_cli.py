import os
import importlib
import tempfile
import unittest
from keyword import kwlist
from unittest import mock
import warnings
import logging
from unittest.mock import patch
from addons_installer import addons_installer

from odoo.addons.odoo_custom_server.cli.web_server import WebServer
from odoo.addons.odoo_custom_server.command_server import OdooPatchedServer

try:
    import odoo
    from odoo.cli import command as odoo_command
    from odoo.tools import config
    from odoo.addons.odoo_custom_server import cli  # noqa
    skip = False
except ImportError:
    skip = True

_logger = logging.getLogger(__name__)

@unittest.skipIf(skip,f"Not in Odoo Env, can't import odoo")
class TestOdooCommand(unittest.TestCase):

    def setUp(self):
        fd, path = tempfile.mkstemp()
        self._tmp_path = path
        _logger.info("Odoo config %s", self._tmp_path)
        self.patch_env = patch.dict(os.environ, {"ODOO_RC": str(path)})
        self.patch_env.start()
        warnings.filterwarnings("ignore", category=ResourceWarning) # Odoo don't close pointer to config file !!!

    def tearDown(self):
        os.unlink(self._tmp_path)
        self.patch_env.stop()

    def test_pack(self):
        def _(to, *args, **kwargs):
            return to, args, kwargs
        args = ["titi"]
        kwargs = {"tf":"toto"}
        to, _args, _kwargs = _(*args, **kwargs)
        self.assertEqual("titi", to)
        self.assertFalse(_args)
        self.assertEqual(_kwargs, kwargs)

    def assert_wrapped(self):
        import odoo.cli.server
        self.assertTrue(hasattr(odoo.cli.server.report_configuration, "__wrapped__"), msg="`__wrapped__` mean wrapt patch this function")
        import odoo.service.db
        self.assertTrue(hasattr(odoo.service.db._create_empty_database, "__wrapped__"), msg="`__wrapped__` mean wrapt patch this function")
        self.assertTrue(hasattr(odoo.service.db.list_dbs, "__wrapped__"), msg="`__wrapped__` mean wrapt patch this function")
        import odoo.sql_db
        self.assertTrue(hasattr(odoo.sql_db.connection_info_for, "__wrapped__"), msg="`__wrapped__` mean wrapt patch this function")

    @patch.dict(os.environ, {"DB_NAME": "foo"})
    def test_web_server(self):
        """ Check web_server has called the start method of odoo with stop False and db_name in preload"""
        self.assertIn("web_server", odoo_command.commands)
        inst_clazz = odoo.cli.command.commands["web_server"]()
        OdooPatchedServer._exit=False
        with patch.object(odoo.service.server, "start") as start_mock:
            inst_clazz.run([])
            self.assertEqual(1, start_mock.call_count)
            _, kwargs = start_mock.call_args
            self.assertEqual(kwargs.get("preload"), ["foo"])
            self.assertEqual(kwargs.get("stop"), False)


    @patch.dict(os.environ, {"UPDATE": "module_update", "INSTALL": "modules", "DB_NAME": "foo"})
    def test_update_server(self):
        """ Check update_server runs odoo start command with stop=True, init and update configured """
        self.assertIn("update_server", odoo_command.commands)
        inst_clazz = odoo.cli.command.commands["update_server"]()
        OdooPatchedServer._exit=False
        with patch.object(odoo.service.server, "start") as start_mock:
            inst_clazz.run([])
            self.assertEqual(1, start_mock.call_count)
            self.assertEqual(odoo.tools.config["db_name"], "foo")
            _, kwargs = start_mock.call_args
            self.assertEqual(kwargs.get("preload"), ["foo"])
            self.assertEqual(kwargs.get("stop"), True)
            self.assertEqual(odoo.tools.config["update"], {'module_update': 1})
            self.assertEqual(odoo.tools.config["init"], {"modules": 1})

    @patch.dict(os.environ, {"DB_NAME": "foo"})
    def test_generic_server(self):
        """
        Assert the generic_server runs odoo start command with stop=False, db_name in preload
        """
        self.assertIn("generic_server", odoo_command.commands)
        inst_clazz = odoo.cli.command.commands["generic_server"]()
        OdooPatchedServer._exit=False
        with patch.object(odoo.service.server, "start") as start_mock:
            assert inst_clazz.get_runner()._exit==False
            inst_clazz.run([])
            self.assertEqual(1, start_mock.call_count)
            _, kwargs = start_mock.call_args
            self.assertEqual(kwargs.get("preload"), ["foo"])
            self.assertEqual(kwargs.get("stop"), False)

    @patch.dict(os.environ, {
        "ADDONS_GIT_DEFAULT_SERVER": "github.com",
        "ADDONS_GIT_DEFAULT_PROTOCOLE": "public",
        "ADDONS_GIT_REPO1": "OCA/web",
        "DEPOT_GIT" : "-b production --single-branch --depth=1 https://$(HTTPS_USER_DEPOT_GIT):$(HTTPS_PASSWORD_DEPOT_GIT)@gitlab.mangono.io/odoo/v15/issues.git",
        "HTTPS_PASSWORD_DEPOT_GIT": "__password__",
        "HTTPS_USER_DEPOT_GIT": "__user__",
        "DB_NAME": "foo",
    })
    def test_generic_server_install(self):
        """
        Assert the `run` function of the dynamic odoo.cli.Command call
        1. the save function of the config
        2. the install function of addon-installer to install the addons
        """
        self.assertIn("generic_server", odoo_command.commands)
        inst_clazz = odoo.cli.command.commands["generic_server"]()
        OdooPatchedServer._exit=False
        with patch.object(addons_installer.AddonsInstaller, "install") as installer_mock:
            with patch.object(odoo.cli.server, "main") as main_server:
                with patch.object(config, "_parse_config") as parse_args_mock:
                    with patch.object(config, "save") as save_mock:
                        with patch.object(odoo.service.server, "start") as start_mock:
                            inst_clazz.run([])
        self.assertTrue(installer_mock.call_count>= 2, "install REPO1 and DEPOT_GIT + local when running in odoo image")
        save_mock.assert_called_once()


    @mock.patch.dict(os.environ, {"ODOO_CUSTOM_SERVER_DISABLE_PATCH": "True"})
    def test_no_patch(self):
        """ Check disabling of odoo patching by env variable """
        runner = WebServer().get_runner()
        runner.load_env_config()
        OdooPatchedServer._exit=False
        with patch.object(odoo.service.server, "start") as start_mock:
            with patch.object(importlib.metadata.EntryPoint, "load") as load_mock:
                runner.execute_command([""])
        load_mock.assert_not_called()
