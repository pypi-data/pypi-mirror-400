from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x58747131, name="types.Poll")
class Poll(TLObject):
    id: Long = TLField()
    flags: Int = TLField(is_flags=True)
    closed: bool = TLField(flag=1 << 0)
    public_voters: bool = TLField(flag=1 << 1)
    multiple_choice: bool = TLField(flag=1 << 2)
    quiz: bool = TLField(flag=1 << 3)
    question: TLObject = TLField()
    answers: list[TLObject] = TLField()
    close_period: Optional[Int] = TLField(flag=1 << 4)
    close_date: Optional[Int] = TLField(flag=1 << 5)
