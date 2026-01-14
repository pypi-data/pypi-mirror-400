from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcc30290b, name="functions.messages.ForwardMessages_135")
class ForwardMessages_135(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    background: bool = TLField(flag=1 << 6)
    with_my_score: bool = TLField(flag=1 << 8)
    drop_author: bool = TLField(flag=1 << 11)
    drop_media_captions: bool = TLField(flag=1 << 12)
    from_peer: TLObject = TLField()
    id: list[Int] = TLField()
    random_id: list[Long] = TLField()
    to_peer: TLObject = TLField()
    schedule_date: Optional[Int] = TLField(flag=1 << 10)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
