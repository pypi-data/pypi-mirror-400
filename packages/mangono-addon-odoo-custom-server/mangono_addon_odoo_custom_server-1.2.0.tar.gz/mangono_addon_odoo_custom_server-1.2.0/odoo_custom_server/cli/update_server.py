from __future__ import annotations

import logging

from environ_odoo_config._odoo_command import OdooCommand

from odoo.addons.odoo_custom_server.command_server import OdooPatchedServer

_logger = logging.getLogger("web_server")


class _InternalUpdateServer(OdooPatchedServer):
    def do_somethings(self) -> bool:
        if not self.env_config.update_init.update and not self.env_config.update_init.install:
            _logger.error("Nothing to do, $INSTALL and $UPDATE are empty !!!!!!!")
            return False
        return True

    def load_env_config(self):
        _logger.info("Start Odoo in Update/Init mode")
        super().load_env_config()
        self.env_config.misc.stop_after_init = True
        self.env_config.http.enable = False


class UpgradeServer(OdooCommand):
    """
    Run Odoo in update/init mode, apply patch and then run the server
    """

    name = "update_server"

    def get_runner(self) -> OdooPatchedServer:
        return _InternalUpdateServer(apply_patcher=True)

    def run(self, args):
        self.get_runner().execute_command(args)
