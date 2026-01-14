from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3a836df8, name="types.SponsoredMessage_136")
class SponsoredMessage_136(TLObject):
    flags: Int = TLField(is_flags=True)
    recommended: bool = TLField(flag=1 << 5)
    random_id: bytes = TLField()
    from_id: Optional[TLObject] = TLField(flag=1 << 3)
    chat_invite: Optional[TLObject] = TLField(flag=1 << 4)
    chat_invite_hash: Optional[str] = TLField(flag=1 << 4)
    channel_post: Optional[Int] = TLField(flag=1 << 2)
    start_param: Optional[str] = TLField(flag=1 << 0)
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
