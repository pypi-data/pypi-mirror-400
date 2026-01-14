from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd069ccde, name="functions.stories.StartLive")
class StartLive(TLObject):
    flags: Int = TLField(is_flags=True)
    pinned: bool = TLField(flag=1 << 2)
    noforwards: bool = TLField(flag=1 << 4)
    rtmp_stream: bool = TLField(flag=1 << 5)
    peer: TLObject = TLField()
    caption: Optional[str] = TLField(flag=1 << 0)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    privacy_rules: list[TLObject] = TLField()
    random_id: Long = TLField()
    messages_enabled: bool = TLField(flag=1 << 6, flag_serializable=True)
    send_paid_messages_stars: Optional[Long] = TLField(flag=1 << 7)
