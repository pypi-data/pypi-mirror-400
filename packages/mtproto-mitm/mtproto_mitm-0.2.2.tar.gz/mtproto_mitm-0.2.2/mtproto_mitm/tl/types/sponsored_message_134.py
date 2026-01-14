from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd151e19a, name="types.SponsoredMessage_134")
class SponsoredMessage_134(TLObject):
    flags: Int = TLField(is_flags=True)
    random_id: bytes = TLField()
    from_id: TLObject = TLField()
    channel_post: Optional[Int] = TLField(flag=1 << 2)
    start_param: Optional[str] = TLField(flag=1 << 0)
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
