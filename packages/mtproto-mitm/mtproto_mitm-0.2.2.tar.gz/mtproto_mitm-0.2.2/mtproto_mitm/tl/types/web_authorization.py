from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa6f8f452, name="types.WebAuthorization")
class WebAuthorization(TLObject):
    hash: Long = TLField()
    bot_id: Long = TLField()
    domain: str = TLField()
    browser: str = TLField()
    platform: str = TLField()
    date_created: Int = TLField()
    date_active: Int = TLField()
    ip: str = TLField()
    region: str = TLField()
