from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x780a0310, name="types.help.TermsOfService")
class TermsOfService(TLObject):
    flags: Int = TLField(is_flags=True)
    popup: bool = TLField(flag=1 << 0)
    id: TLObject = TLField()
    text: str = TLField()
    entities: list[TLObject] = TLField()
    min_age_confirm: Optional[Int] = TLField(flag=1 << 1)
