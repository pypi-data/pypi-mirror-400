from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa4bcc6fe, name="types.updates.ChannelDifferenceTooLong")
class ChannelDifferenceTooLong(TLObject):
    flags: Int = TLField(is_flags=True)
    final: bool = TLField(flag=1 << 0)
    timeout: Optional[Int] = TLField(flag=1 << 1)
    dialog: TLObject = TLField()
    messages: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
