from __future__ import annotations

import logging

import wrapt

from odoo import http, release
from odoo.http import request

MAJOR = release.series
_logger = logging.getLogger("odoo.session.REDIS")


def _update_expiration():
    if (
        hasattr(http.root.session_store, "update_expiration")
        and request
        and request.session
        and request.session.uid
        and not request.env["res.users"].browse(request.session.uid)._is_public()
    ):
        http.root.session_store.update_expiration(request.session)


if MAJOR >= "19.0":

    @wrapt.patch_function_wrapper(
        "odoo.addons.base.models.ir_http",
        "IrHttp._authenticate",
    )
    def _patch_from_attachment(wrapped, instance, args, kwargs):
        _update_expiration()
        return wrapped(*args, **kwargs)
else:

    @wrapt.patch_function_wrapper("odoo.addons.base", "models.ir_http.IrHttp._authenticate")
    def _patch_from_attachment(wrapped, instance, args, kwargs):
        _update_expiration()
        return wrapped(*args, **kwargs)
