from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x25d8c1d8, name="types.InputInvoiceStarGift_189")
class InputInvoiceStarGift_189(TLObject):
    flags: Int = TLField(is_flags=True)
    hide_name: bool = TLField(flag=1 << 0)
    user_id: TLObject = TLField()
    gift_id: Long = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
