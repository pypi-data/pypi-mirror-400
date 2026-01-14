from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc661bbc4, name="functions.messages.ForwardMessages_148")
class ForwardMessages_148(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    background: bool = TLField(flag=1 << 6)
    with_my_score: bool = TLField(flag=1 << 8)
    drop_author: bool = TLField(flag=1 << 11)
    drop_media_captions: bool = TLField(flag=1 << 12)
    noforwards: bool = TLField(flag=1 << 14)
    from_peer: TLObject = TLField()
    id: list[Int] = TLField()
    random_id: list[Long] = TLField()
    to_peer: TLObject = TLField()
    top_msg_id: Optional[Int] = TLField(flag=1 << 9)
    schedule_date: Optional[Int] = TLField(flag=1 << 10)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
