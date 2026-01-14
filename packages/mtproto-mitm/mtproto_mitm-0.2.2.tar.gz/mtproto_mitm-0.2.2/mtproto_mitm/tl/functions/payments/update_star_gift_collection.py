from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4fddbee7, name="functions.payments.UpdateStarGiftCollection")
class UpdateStarGiftCollection(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    collection_id: Int = TLField()
    title: Optional[str] = TLField(flag=1 << 0)
    delete_stargift: Optional[list[TLObject]] = TLField(flag=1 << 1)
    add_stargift: Optional[list[TLObject]] = TLField(flag=1 << 2)
    order: Optional[list[TLObject]] = TLField(flag=1 << 3)
