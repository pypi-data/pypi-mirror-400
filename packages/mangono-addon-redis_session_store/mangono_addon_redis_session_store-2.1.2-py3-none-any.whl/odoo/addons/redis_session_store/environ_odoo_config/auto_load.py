from environ_odoo_config.environ import Environ

from odoo.addons.redis_session_store.env_config import RedisEnvConfig


def auto_load_redis_session_store(environ: Environ) -> bool:
    redis_config = RedisEnvConfig(environ)
    return redis_config.enable
