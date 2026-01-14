from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3f56aea3, name="types.payments.PaymentForm_65")
class PaymentForm_65(TLObject):
    flags: Int = TLField(is_flags=True)
    can_save_credentials: bool = TLField(flag=1 << 2)
    password_missing: bool = TLField(flag=1 << 3)
    bot_id: Int = TLField()
    invoice: TLObject = TLField()
    provider_id: Int = TLField()
    url: str = TLField()
    native_provider: Optional[str] = TLField(flag=1 << 4)
    native_params: Optional[TLObject] = TLField(flag=1 << 4)
    saved_info: Optional[TLObject] = TLField(flag=1 << 0)
    saved_credentials: Optional[TLObject] = TLField(flag=1 << 1)
    users: list[TLObject] = TLField()
