import unittest
import environ_odoo_config
import psycopg2
from unittest import mock
from unittest.mock import patch
import os
from odoo_custom_server.odoo_patch.sql_db import _patch_db_connect, _patch_connection_info_for
try:
    from odoo_custom_server import command_server
    import odoo
    from odoo import modules
    from odoo import sql_db
    odoo_ok = True
except ImportError:
    odoo_ok = False

@unittest.skipUnless(odoo_ok, reason="Need odoo importable")
class Test1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        command_server._auto_load_entry_point()

    def test_raise_not_valid_db(self):
        with self.assertRaises(Exception):
            modules.registry.Registry("not_a_valid_db_name")

    def test_connection_info_for_wrapped(self):
        self.assertTrue(hasattr(odoo.sql_db.connection_info_for, "__wrapped__"))

    def test_db_connect_wrapped(self):
        self.assertTrue(hasattr(odoo.sql_db.db_connect, "__wrapped__"))

    def test_connect_postgres(self):
        with patch.object(environ_odoo_config.odoo_utils, "get_config_db_names", return_value=["base1"]):
            connection = sql_db.db_connect("postgres")
        self.assertEqual(connection.dbname, "base1")

class TestDbConnect(unittest.TestCase):
    def test_db_connect_not_in_config(self):
        """ Not allowed to connect to a base not listed in configuration """
        with patch.object(environ_odoo_config.odoo_utils, "get_config_db_names", return_value=["base1"]):
            fake_db_connect = mock.MagicMock()
            with self.assertRaises(psycopg2.OperationalError):
                _patch_db_connect(fake_db_connect, None, ["mybase"], {})

    def test_db_connect_in_config(self):
        """ It is allowed to connect to a base listed in configuration """
        with patch.object(environ_odoo_config.odoo_utils, "get_config_db_names", return_value=["base1", "base2"]):
            fake_db_connect = mock.MagicMock()
            _patch_db_connect(fake_db_connect, None, ["base2"], {})
            fake_db_connect.assert_called_once()
            fake_db_connect.assert_called_with("base2")

    def test_db_connect_to_postres_rerouting(self):
        """ Connexion trial to postgres is rerouted to first database listed in configuration """
        with patch.object(environ_odoo_config.odoo_utils, "get_config_db_names", return_value=["base1", "base2"]):
            fake_db_connect = mock.MagicMock()
            _patch_db_connect(fake_db_connect, None, ["postgres"], {})
            fake_db_connect.assert_called_once()
            fake_db_connect.assert_called_with("base1")

    def test_db_connect_no_config(self):
        """ No base listed in configuration => connexion trials to the base"""
        with patch.object(environ_odoo_config.odoo_utils, "get_config_db_names", return_value=[]) as get_config_db_names_mock:
            fake_db_connect = mock.MagicMock()
            _patch_db_connect(fake_db_connect, None, ["base3"], {})
            fake_db_connect.assert_called_once()
            fake_db_connect.assert_called_with("base3")

class TestConnexionInfoFor(unittest.TestCase):
    def test_fallback(self):
        fake_connexion_info_for = mock.MagicMock(return_value=("base1",{}))
        db_name, connexion_info = _patch_connection_info_for(fake_connexion_info_for, None,  [], {})
        self.assertEqual(db_name, "base1")
        self.assertTrue(connexion_info["fallback_application_name"].startswith("odoo-"))

    @patch.dict(os.environ, {"PGAPPNAME": "foo {pid}"})
    def test_app_name(self):
        """ La valeur de l'env PGAPPNAME est prise en compte avec le PID rempli """
        fake_connexion_info_for = mock.MagicMock(return_value=("base1", {}))
        db_name, connexion_info = _patch_connection_info_for(fake_connexion_info_for, None, [], {})
        self.assertEqual(db_name, "base1")
        self.assertTrue(connexion_info["application_name"].startswith("foo"))
        self.assertRegex(connexion_info["application_name"], r"^foo \d*")

    @patch.dict(os.environ, {"ODOO_PGAPPNAME": "foo {pid}"})
    def test_odoo_app_name(self):
        """ La valeur de l'env ODOO_PGAPPNAME est prise en compte avec le PID rempli """
        fake_connexion_info_for = mock.MagicMock(return_value=("base1", {}))
        db_name, connexion_info = _patch_connection_info_for(fake_connexion_info_for, None, [], {})
        self.assertEqual(db_name, "base1")
        self.assertTrue(connexion_info["application_name"].startswith("foo"))
        self.assertRegex(connexion_info["application_name"], r"^foo \d*")
