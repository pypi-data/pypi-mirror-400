from __future__ import annotations

import redis
from environ_odoo_config.config_section.api import OdooConfigGroup, RepeatableKey, SimpleKey

DEFAULT_SESSION_TIMEOUT = 60 * 60 * 24 * 3  # 3 days in seconds
DEFAULT_SESSION_TIMEOUT_ANONYMOUS = 60 * 2  # 2 minutes in seconds
DEFAULT_SESSION_TIMEOUT_ON_INACTIVITY = "True"
DEFAULT_SESSION_TIMEOUT_IGNORED_URLS = ["/longpolling", "/calendar/notify"]


class RedisEnvConfig(OdooConfigGroup):
    _ini_section = "redis_session"

    host: str = SimpleKey("REDIS_HOST", ini_dest="redis_host", py_default="localhost")
    port: int = SimpleKey("REDIS_PORT", ini_dest="redis_port", py_default=6379)
    prefix: str = SimpleKey("REDIS_PREFIX", ini_dest="redis_prefix")
    url: str = SimpleKey("REDIS_URL", ini_dest="redis_url")
    password: str = SimpleKey("REDIS_PASSWORD", ini_dest="redis_password")
    redis_ssl: bool = SimpleKey(
        "REDIS_SSL",
        ini_dest="redis_ssl",
        py_default=True,
    )
    expiration: int = SimpleKey(
        "ODOO_SESSION_REDIS_EXPIRATION", ini_dest="redis_expiration", py_default=DEFAULT_SESSION_TIMEOUT
    )
    anon_expiration: int = SimpleKey(
        "ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS",
        ini_dest="redis_anon_expiration",
        py_default=DEFAULT_SESSION_TIMEOUT_ANONYMOUS,
    )
    timeout_on_inactivity: bool = SimpleKey(
        "ODOO_SESSION_REDIS_TIMEOUT_ON_INACTIVITY",
        ini_dest="redis_timeout_on_inactivity",
        py_default=DEFAULT_SESSION_TIMEOUT_ON_INACTIVITY,
    )
    ignored_urls: set[str] = RepeatableKey(
        "ODOO_SESSION_REDIS_TIMEOUT_IGNORED_URLS",
        ini_dest="redis_ignored_urls",
        ini_default=DEFAULT_SESSION_TIMEOUT_IGNORED_URLS,
    )
    db: int = SimpleKey("REDIS_DB_INDEX", py_default=0)
    disable_gc: bool = SimpleKey("ODOO_DISABLE_SESSION_GC")

    @property
    def enable(self) -> bool:
        return bool(self.host and self.password)

    def connect(self) -> redis.Redis:
        """
        Return the connection to the Redis server.
        If `self.url` is filled, then `url` all other connection info are exclude.

        expiration, and anon_expiration are not passed to the connection.

        :return: A connection to the Redis server.
        """
        if self.url:
            return redis.Redis.from_url(self.url)
        return redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            ssl=self.redis_ssl,
        )
