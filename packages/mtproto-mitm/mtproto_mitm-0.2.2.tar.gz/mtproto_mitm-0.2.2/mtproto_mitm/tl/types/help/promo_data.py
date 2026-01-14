from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8a4d87a, name="types.help.PromoData")
class PromoData(TLObject):
    flags: Int = TLField(is_flags=True)
    proxy: bool = TLField(flag=1 << 0)
    expires: Int = TLField()
    peer: Optional[TLObject] = TLField(flag=1 << 3)
    psa_type: Optional[str] = TLField(flag=1 << 1)
    psa_message: Optional[str] = TLField(flag=1 << 2)
    pending_suggestions: list[str] = TLField()
    dismissed_suggestions: list[str] = TLField()
    custom_pending_suggestion: Optional[TLObject] = TLField(flag=1 << 4)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
