from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc02c4f4b, name="types.StarGiftAttributeOriginalDetails_196")
class StarGiftAttributeOriginalDetails_196(TLObject):
    flags: Int = TLField(is_flags=True)
    sender_id: Optional[Long] = TLField(flag=1 << 0)
    recipient_id: Long = TLField()
    date: Int = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
