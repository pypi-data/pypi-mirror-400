from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x94a495c3, name="functions.messages.GetQuickReplyMessages")
class GetQuickReplyMessages(TLObject):
    flags: Int = TLField(is_flags=True)
    shortcut_id: Int = TLField()
    id: Optional[list[Int]] = TLField(flag=1 << 0)
    hash: Long = TLField()
