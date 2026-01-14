from __future__ import annotations

import os
import unittest
from typing import Type, Any, Set, Dict
from unittest import mock

try:
    from odoo_custom_server import command_server
    from odoo_custom_server.cli.update_server import UpgradeServer
    from odoo_custom_server.cli.web_server import WebServer
    from odoo_custom_server.cli.generic_server import GenericServer
    from odoo_custom_server.command_server import OdooPatchedServer
    from environ_odoo_config.odoo_config import OdooEnvConfig
    skip=False
except ImportError:
    skip = True

ODOO_VERSION = str(os.getenv("ODOO_VERSION", "12.0"))
"""Force set to 12.0, otherwise use environ value, usefull when running the test inside the odoo-cloud docker image"""


@unittest.skipIf(skip,f"Not in Odoo Env, can't import odoo")
class TestServerClazzStruct(unittest.TestCase):
    def get_commands(self) -> dict[str, Any]:
        import odoo.cli.command
        return odoo.cli.command.commands

    def assertClassEqual(self, class1: type, class2: type):
        # impossible d'utiliser Is ou bien issubclass car les 2 classes sont importée de modules différents
        self.assertEqual(class1.__name__, class2.__name__)
        self.assertEqual(
            set(dir(class1)),
            set(dir(class2))
        )

    def assert_command_correct_mro(self, cmd_to_assert: Type[command_server.OdooPatchedServer], expected_name: str):
        self.assertIs(cmd_to_assert, command_server.OdooPatchedServer)
        self.assertEqual(expected_name, cmd_to_assert.name, "Ensure the command name")

    def test_cli_mro_and_name_ok(self):
        commands = self.get_commands()
        self.assertClassEqual(commands.get("update_server"), UpgradeServer)
        self.assertClassEqual(commands.get("generic_server"), GenericServer)
        self.assertClassEqual(commands.get("web_server"), WebServer)

    def test_auto_register(self):
        command_names = list(self.get_commands().keys())
        self.assertIn("update_server", command_names)
        self.assertIn("generic_server", command_names)
        self.assertIn("web_server", command_names)


@unittest.skipIf(skip,f"Not in Odoo Env, can't import odoo")
@mock.patch.dict(os.environ, {"ODOO_VERSION": ODOO_VERSION})
class TestCliTestServer(unittest.TestCase):

    def assert_runner(self, runner: OdooPatchedServer, update:Set[str], install:Set[str], msg:str):
        runner.load_env_config()
        self.assertTrue(runner.env_config.misc.stop_after_init)
        self.assertFalse(runner.env_config.http.enable)
        self.assertEqual(runner.env_config.update_init.update, update)
        self.assertEqual(runner.env_config.update_init.install, install)
        self.assertEqual(runner.do_somethings(), bool(update or install))

    def test_convert_to_args_update_server(self):
        self.assert_runner(
            UpgradeServer().get_runner(),
            update=set(),
            install=set(),
            msg="Always stop-after-init and no-http",
        )

        with mock.patch.dict(os.environ, STOP_AFTER_INIT=str(False)):
            self.assert_runner(
                UpgradeServer().get_runner(),
                update=set(),
                install=set(),
                msg="Always stop-after-init and no-http",
            )

        with mock.patch.dict(os.environ, HTTP_ENABLE=str(True)):
            self.assert_runner(
                UpgradeServer().get_runner(),
                update=set(),
                install=set(),
                msg="Always stop-after-init and no-http",
            )

    def test_update(self):
        with mock.patch.dict(os.environ, UPDATE_1="base", UPDATE_2="module1,module2"):
            self.assert_runner(
                UpgradeServer().get_runner(),
                update={"base", "module1", "module2"},
                install=set(),
                msg="Always stop-after-init and no-http",
            )

    def test_install(self):
        with mock.patch.dict(os.environ, INSTALL_1="module0", INSTALL_2="module1,module2"):
            self.assert_runner(
                UpgradeServer().get_runner(),
                update=set(),
                install={"module0", "module1", "module2"},
                msg="Always stop-after-init and no-http",
            )
