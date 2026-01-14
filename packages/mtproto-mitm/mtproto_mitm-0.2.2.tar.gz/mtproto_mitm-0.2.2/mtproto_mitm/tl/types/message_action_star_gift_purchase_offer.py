from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x774278d4, name="types.MessageActionStarGiftPurchaseOffer")
class MessageActionStarGiftPurchaseOffer(TLObject):
    flags: Int = TLField(is_flags=True)
    accepted: bool = TLField(flag=1 << 0)
    declined: bool = TLField(flag=1 << 1)
    gift: TLObject = TLField()
    price: TLObject = TLField()
    expires_at: Int = TLField()
