from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3076c4bf, name="functions.account.UnregisterDevice_75")
class UnregisterDevice_75(TLObject):
    token_type: Int = TLField()
    token: str = TLField()
    other_uids: list[Int] = TLField()
