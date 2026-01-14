from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xebe46819, name="types.UpdateServiceNotification")
class UpdateServiceNotification(TLObject):
    flags: Int = TLField(is_flags=True)
    popup: bool = TLField(flag=1 << 0)
    invert_media: bool = TLField(flag=1 << 2)
    inbox_date: Optional[Int] = TLField(flag=1 << 1)
    type_: str = TLField()
    message: str = TLField()
    media: TLObject = TLField()
    entities: list[TLObject] = TLField()
