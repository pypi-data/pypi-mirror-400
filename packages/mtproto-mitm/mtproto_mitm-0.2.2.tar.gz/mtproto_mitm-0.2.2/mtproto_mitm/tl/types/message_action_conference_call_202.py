from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xff397dea, name="types.MessageActionConferenceCall_202")
class MessageActionConferenceCall_202(TLObject):
    flags: Int = TLField(is_flags=True)
    missed: bool = TLField(flag=1 << 0)
    active: bool = TLField(flag=1 << 1)
    call_id: Long = TLField()
    slug: str = TLField()
    duration: Optional[Int] = TLField(flag=1 << 2)
    other_participants: Optional[list[TLObject]] = TLField(flag=1 << 3)
