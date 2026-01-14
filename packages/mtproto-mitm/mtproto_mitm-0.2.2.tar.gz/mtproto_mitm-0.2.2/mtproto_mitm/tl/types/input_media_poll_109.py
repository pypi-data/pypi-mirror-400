from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xabe9ca25, name="types.InputMediaPoll_109")
class InputMediaPoll_109(TLObject):
    flags: Int = TLField(is_flags=True)
    poll: TLObject = TLField()
    correct_answers: Optional[list[bytes]] = TLField(flag=1 << 0)
