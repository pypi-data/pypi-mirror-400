from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8a333c8d, name="functions.payments.GetPaymentForm_128")
class GetPaymentForm_128(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    theme_params: Optional[TLObject] = TLField(flag=1 << 0)
