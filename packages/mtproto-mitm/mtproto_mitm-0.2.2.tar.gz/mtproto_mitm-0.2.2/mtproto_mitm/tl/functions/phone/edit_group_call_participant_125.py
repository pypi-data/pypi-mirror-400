from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd975eb80, name="functions.phone.EditGroupCallParticipant_125")
class EditGroupCallParticipant_125(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    call: TLObject = TLField()
    participant: TLObject = TLField()
    volume: Optional[Int] = TLField(flag=1 << 1)
    raise_hand: bool = TLField(flag=1 << 2, flag_serializable=True)
