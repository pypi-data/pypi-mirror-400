from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8c39793f, name="types.help.PromoData_113")
class PromoData_113(TLObject):
    flags: Int = TLField(is_flags=True)
    proxy: bool = TLField(flag=1 << 0)
    expires: Int = TLField()
    peer: TLObject = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    psa_type: Optional[str] = TLField(flag=1 << 1)
    psa_message: Optional[str] = TLField(flag=1 << 2)
