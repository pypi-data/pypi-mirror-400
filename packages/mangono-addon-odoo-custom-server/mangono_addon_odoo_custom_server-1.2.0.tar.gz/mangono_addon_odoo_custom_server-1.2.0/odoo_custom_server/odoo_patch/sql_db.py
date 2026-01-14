import logging
import os
import warnings

import odoo
import odoo.tools
import psycopg2
import wrapt
from environ_odoo_config import odoo_utils

_logger = logging.getLogger(__name__)


def patch_connection_info_for():
    return wrapt.wrap_function_wrapper("odoo.sql_db", "connection_info_for", _patch_connection_info_for)


def patch_db_connect():
    return wrapt.wrap_function_wrapper("odoo.sql_db", "db_connect", _patch_db_connect)


def _patch_connection_info_for(wrapped, instance, args, kwargs):
    """Add a nice app_name including pid"""
    db_name, connection_info = wrapped(*args, **kwargs)
    app_name = odoo.tools.config.options.get("db_app_name") or os.getenv(
        "PGAPPNAME"
    )  # Don't exist in version less than 19.0
    if "ODOO_PGAPPNAME" in os.environ and not app_name:
        warnings.warn("use PGAPPNAME instead of ODOO_PGAPPNAME", DeprecationWarning, 2)
        app_name = os.environ["ODOO_PGAPPNAME"]
    pid = str(os.getpid())
    connection_info["fallback_application_name"] = f"odoo-{pid}"
    if app_name:
        # Using manual string interpolation for security reason and trimming at default NAMEDATALEN=63
        connection_info["application_name"] = app_name.replace("{pid}", pid)[:63]
    return db_name, connection_info


def _patch_db_connect(wrapped, instance, args, kwargs):
    """Logic :
    Whene configuration of databases names is done, allows only connexion to database listed in configuration
    connexion to postgres will be rerouted to first database in configuration
    OperationalError raised otherwise
    """

    def _(to, *args, **kwargs):
        return to, args, kwargs

    to, _args, _kwargs = _(*args, **kwargs)
    conf_db_names = odoo_utils.get_config_db_names(odoo.tools.config)

    if not conf_db_names or to in conf_db_names:
        return wrapped(*args, **kwargs)
    # With this patch we never connect to "postgres" database
    # Connect to "postgres" is a bad practice, and not allowed on many DBSaas provider
    # Odoo don't really need it, so we return the first one.
    if to == "postgres":
        return wrapped(conf_db_names[0], *_args, **_kwargs)

    # The database asked to connect to is not in the allowed list, we raise an error
    raise psycopg2.OperationalError(f"Database {to} not exist")
