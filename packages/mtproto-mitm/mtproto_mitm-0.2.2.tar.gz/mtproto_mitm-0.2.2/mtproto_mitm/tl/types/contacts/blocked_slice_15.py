from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x900802a1, name="types.contacts.BlockedSlice_15")
class BlockedSlice_15(TLObject):
    count: Int = TLField()
    blocked: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
