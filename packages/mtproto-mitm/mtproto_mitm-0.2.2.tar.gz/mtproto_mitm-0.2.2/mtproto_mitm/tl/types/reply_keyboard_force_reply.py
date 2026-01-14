from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x86b40b08, name="types.ReplyKeyboardForceReply")
class ReplyKeyboardForceReply(TLObject):
    flags: Int = TLField(is_flags=True)
    single_use: bool = TLField(flag=1 << 1)
    selective: bool = TLField(flag=1 << 2)
    placeholder: Optional[str] = TLField(flag=1 << 3)
