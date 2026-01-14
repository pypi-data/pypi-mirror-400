from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcac943f2, name="types.WebAuthorization_76")
class WebAuthorization_76(TLObject):
    hash: Long = TLField()
    bot_id: Int = TLField()
    domain: str = TLField()
    browser: str = TLField()
    platform: str = TLField()
    date_created: Int = TLField()
    date_active: Int = TLField()
    ip: str = TLField()
    region: str = TLField()
