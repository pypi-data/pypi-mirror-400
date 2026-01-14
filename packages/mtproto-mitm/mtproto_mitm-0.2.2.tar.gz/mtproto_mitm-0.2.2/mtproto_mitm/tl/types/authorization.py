from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xad01d61d, name="types.Authorization")
class Authorization(TLObject):
    flags: Int = TLField(is_flags=True)
    current: bool = TLField(flag=1 << 0)
    official_app: bool = TLField(flag=1 << 1)
    password_pending: bool = TLField(flag=1 << 2)
    encrypted_requests_disabled: bool = TLField(flag=1 << 3)
    call_requests_disabled: bool = TLField(flag=1 << 4)
    unconfirmed: bool = TLField(flag=1 << 5)
    hash: Long = TLField()
    device_model: str = TLField()
    platform: str = TLField()
    system_version: str = TLField()
    api_id: Int = TLField()
    app_name: str = TLField()
    app_version: str = TLField()
    date_created: Int = TLField()
    date_active: Int = TLField()
    ip: str = TLField()
    country: str = TLField()
    region: str = TLField()
