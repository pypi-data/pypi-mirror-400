import logging

from environ_odoo_config._odoo_command import OdooCommand
from odoo.addons.odoo_custom_server.command_server import OdooPatchedServer

_logger = logging.getLogger("web_server")


class _InternalWebServer(OdooPatchedServer):
    def load_env_config(self):
        _logger.info("Start Odoo in run mode, remove init and update")
        super().load_env_config()
        # remove update or init that may be present from update_server previous call
        self.env_config.update_init.update = ""
        self.env_config.update_init.init = ""


class WebServer(OdooCommand):
    """
    Run Odoo in web mode, apply patch and then run the server
    """

    name = "web_server"

    def get_runner(self) -> OdooPatchedServer:
        return _InternalWebServer(apply_patcher=True)

    def run(self, args):
        self.get_runner().execute_command(args)
