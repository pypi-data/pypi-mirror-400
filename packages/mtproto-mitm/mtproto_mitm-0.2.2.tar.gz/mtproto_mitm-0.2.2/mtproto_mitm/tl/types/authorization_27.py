from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7bf2e6f6, name="types.Authorization_27")
class Authorization_27(TLObject):
    hash: Long = TLField()
    flags: Int = TLField()
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
