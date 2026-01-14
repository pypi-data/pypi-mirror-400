from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf9a2a6cb, name="types.InputStorePaymentStarsTopup")
class InputStorePaymentStarsTopup(TLObject):
    flags: Int = TLField(is_flags=True)
    stars: Long = TLField()
    currency: str = TLField()
    amount: Long = TLField()
    spend_purpose_peer: Optional[TLObject] = TLField(flag=1 << 0)
