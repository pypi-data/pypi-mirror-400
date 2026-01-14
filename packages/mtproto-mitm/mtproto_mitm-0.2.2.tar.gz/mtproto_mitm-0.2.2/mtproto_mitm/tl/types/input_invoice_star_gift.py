from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe8625e92, name="types.InputInvoiceStarGift")
class InputInvoiceStarGift(TLObject):
    flags: Int = TLField(is_flags=True)
    hide_name: bool = TLField(flag=1 << 0)
    include_upgrade: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    gift_id: Long = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
