from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2a3c381f, name="types.SponsoredMessage_133")
class SponsoredMessage_133(TLObject):
    flags: Int = TLField(is_flags=True)
    random_id: bytes = TLField()
    from_id: TLObject = TLField()
    start_param: Optional[str] = TLField(flag=1 << 0)
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
