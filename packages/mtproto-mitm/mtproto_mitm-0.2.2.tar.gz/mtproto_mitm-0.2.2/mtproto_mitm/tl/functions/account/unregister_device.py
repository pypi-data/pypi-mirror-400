from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6a0d3206, name="functions.account.UnregisterDevice")
class UnregisterDevice(TLObject):
    token_type: Int = TLField()
    token: str = TLField()
    other_uids: list[Long] = TLField()
