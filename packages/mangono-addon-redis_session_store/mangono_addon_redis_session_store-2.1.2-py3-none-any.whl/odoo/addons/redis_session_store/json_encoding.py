from __future__ import annotations

import json
from datetime import date, datetime

import dateutil


def _object_decoder(obj):
    if "_type" not in obj:
        return obj
    type_ = obj["_type"]
    if type_ == "datetime_isoformat":
        return dateutil.parser.parse(obj["value"])
    elif type_ == "date_isoformat":
        return dateutil.parser.parse(obj["value"]).date()
    elif type_ == "set":
        return set(obj["value"])
    return obj


class SessionEncoder(json.JSONEncoder):
    """Encode date/datetime objects

    So that we can later recompose them if they were stored in the session
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return {"_type": "datetime_isoformat", "value": obj.isoformat()}
        elif isinstance(obj, date):
            return {"_type": "date_isoformat", "value": obj.isoformat()}
        elif isinstance(obj, set):
            return {"_type": "set", "value": tuple(obj)}
        return json.JSONEncoder.default(self, obj)


class SessionDecoder(json.JSONDecoder):
    """Decode json, recomposing recordsets and date/datetime"""

    def __init__(self, **kwargs):
        super().__init__(object_hook=_object_decoder, **kwargs)
