from __future__ import annotations

from addons_installer import cli as installer_cli
from environ_odoo_config._odoo_command import OdooCommand

from odoo.addons.odoo_custom_server.command_server import OdooPatchedServer


class GenericServer(OdooCommand):
    """
    Run Odoo, apply patch and install addons and then run the server
    """

    name = "generic_server"

    def get_runner(self) -> OdooPatchedServer:
        return OdooPatchedServer(True)

    def run(self, args: list[str]):
        installer_cli.install_from_env(installer_cli.ArgsCli(all=True, verbose=True))
        self.get_runner().execute_command(args=args)
