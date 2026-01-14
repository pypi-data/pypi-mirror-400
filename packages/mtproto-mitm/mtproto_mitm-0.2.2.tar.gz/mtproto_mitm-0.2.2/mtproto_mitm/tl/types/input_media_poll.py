from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf94e5f1, name="types.InputMediaPoll")
class InputMediaPoll(TLObject):
    flags: Int = TLField(is_flags=True)
    poll: TLObject = TLField()
    correct_answers: Optional[list[bytes]] = TLField(flag=1 << 0)
    solution: Optional[str] = TLField(flag=1 << 1)
    solution_entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
