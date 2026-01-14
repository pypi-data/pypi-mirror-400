from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x66ab0bfc, name="types.phone.GroupCall_122")
class GroupCall_122(TLObject):
    call: TLObject = TLField()
    participants: list[TLObject] = TLField()
    participants_next_offset: str = TLField()
    users: list[TLObject] = TLField()
