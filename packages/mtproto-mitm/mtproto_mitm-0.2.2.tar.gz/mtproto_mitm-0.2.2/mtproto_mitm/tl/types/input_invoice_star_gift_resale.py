from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc39f5324, name="types.InputInvoiceStarGiftResale")
class InputInvoiceStarGiftResale(TLObject):
    flags: Int = TLField(is_flags=True)
    ton: bool = TLField(flag=1 << 0)
    slug: str = TLField()
    to_id: TLObject = TLField()
