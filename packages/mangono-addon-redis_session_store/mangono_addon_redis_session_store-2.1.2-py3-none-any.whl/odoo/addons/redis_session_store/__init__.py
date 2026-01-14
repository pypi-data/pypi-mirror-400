import logging
import random
import os

from functools import cached_property
from environ_odoo_config.environ import Environ

import odoo
from odoo.tools.misc import str2bool
from odoo import http
from . import redis_session
from .env_config import RedisEnvConfig
from .redis_session import RedisSessionStore

_logger = logging.getLogger("odoo.session.REDIS")

try:
    import redis

    _logger.info("Lib redis installed")
except ImportError:
    redis = None

MAJOR = odoo.release.version_info[0]
if MAJOR >= 16:
    from odoo.http import Session as OdooSessionClass
else:
    from odoo.http import OpenERPSession as OdooSessionClass

if MAJOR >= 19:
    from odoo.tools.func import reset_cached_properties
else:
    from odoo.tools.func import lazy_property

    reset_cached_properties = lazy_property.reset_all


def get_server_wide_modules(odoo_version: int):
    """Jusqu'à la v17, les serveurs wide modules se trouvent dans odoo.config.server_wide_modules
    À compter de la v17, il est possible de les récupérer en odoo.tools.config["server_wide_modules"] mais cela est
    nécessaire en v19
    """
    if odoo_version >= 17:
        from odoo.tools import config

        return config["server_wide_modules"]

    else:
        from odoo import conf

        return conf.server_wide_modules


def session_gc(session_store):
    # session_gc is called at setup_session so we keep the randomness bit to only vacuum once in a while.
    if random.random() < 0.001:
        session_store.vacuum()


def _post_load_module():
    if "redis_session_store" not in get_server_wide_modules(MAJOR):
        return
    if not redis:
        raise ImportError("Please install package redis")
    redis_config = RedisEnvConfig(Environ.new())
    server_info = redis_config.connect().info()
    # In case this is a Materia KV Redis compatible database
    if not server_info.get("redis_version") and server_info.get("Materia KV "):
        server_info = {"redis_version": f"Materia KV - {server_info['Materia KV ']}"}
    if not server_info:
        raise ValueError("Can't display server info")
    _logger.info("Redis Session enable [%s]", server_info)
    # Reset the cached property (session_store)
    reset_cached_properties(odoo.http.root)
    type(odoo.http.root).session_store = RedisSessionStore(redis_config, session_class=OdooSessionClass)
    # Keep compatibility with odoo env config.
    # There is no more session_gc global function, so no more patch needed.
    # Now see FilesystemSessionStore#vacuum.
    if MAJOR < 15 and not redis_config.disable_gc:
        odoo.http.session_gc = session_gc
    from . import patcher
