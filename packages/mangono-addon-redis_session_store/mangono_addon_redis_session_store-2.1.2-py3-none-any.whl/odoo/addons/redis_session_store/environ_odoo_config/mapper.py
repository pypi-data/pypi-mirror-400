from __future__ import annotations

from typing import Any

from environ_odoo_config.environ import Environ


def redis_mapper(curr_env: Environ | dict[str, Any]) -> Environ:
    return _kv_clevercloud_redis(Environ(curr_env))


def _kv_clevercloud_redis(curr_env: Environ) -> Environ:
    """ """
    return curr_env + {
        "REDIS_HOST": curr_env.gets("REDIS_HOST", "KV_HOST"),
        "REDIS_PORT": curr_env.gets("REDIS_PORT", "KV_PORT"),
    }
