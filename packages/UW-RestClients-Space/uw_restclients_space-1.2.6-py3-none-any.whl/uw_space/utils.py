# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from dateutil.parser import parse
import pytz
from commonconf import override_settings

fdao_space_override = override_settings(
    RESTCLIENTS_SPACE_DAO_CLASS='Mock')

DEFAULT_TZ = pytz.timezone("America/Los_Angeles")


def str_to_datetime(s):
    if not s:
        return None

    dt = parse(s)

    if dt.tzinfo is None:
        # assume DEFAULT_TZ for naive datetimes
        return dt.replace(tzinfo=DEFAULT_TZ)
    else:
        # convert to DEFAULT_TZ
        return dt.astimezone(DEFAULT_TZ)


def date_to_str(dt):
    return str(dt) if dt is not None else None
