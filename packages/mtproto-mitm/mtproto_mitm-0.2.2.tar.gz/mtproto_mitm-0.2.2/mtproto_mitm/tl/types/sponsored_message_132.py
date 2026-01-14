from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf671f0d1, name="types.SponsoredMessage_132")
class SponsoredMessage_132(TLObject):
    flags: Int = TLField(is_flags=True)
    random_id: bytes = TLField()
    peer_id: TLObject = TLField()
    from_id: TLObject = TLField()
    message: str = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 0)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
