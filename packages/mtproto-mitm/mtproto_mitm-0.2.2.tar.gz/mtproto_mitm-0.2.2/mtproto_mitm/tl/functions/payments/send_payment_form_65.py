from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2b8879b3, name="functions.payments.SendPaymentForm_65")
class SendPaymentForm_65(TLObject):
    flags: Int = TLField(is_flags=True)
    msg_id: Int = TLField()
    requested_info_id: Optional[str] = TLField(flag=1 << 0)
    shipping_option_id: Optional[str] = TLField(flag=1 << 1)
    credentials: TLObject = TLField()
