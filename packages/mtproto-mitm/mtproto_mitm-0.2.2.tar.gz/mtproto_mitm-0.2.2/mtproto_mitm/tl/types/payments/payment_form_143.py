from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb0133b37, name="types.payments.PaymentForm_143")
class PaymentForm_143(TLObject):
    flags: Int = TLField(is_flags=True)
    can_save_credentials: bool = TLField(flag=1 << 2)
    password_missing: bool = TLField(flag=1 << 3)
    form_id: Long = TLField()
    bot_id: Long = TLField()
    title: str = TLField()
    description: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 5)
    invoice: TLObject = TLField()
    provider_id: Long = TLField()
    url: str = TLField()
    native_provider: Optional[str] = TLField(flag=1 << 4)
    native_params: Optional[TLObject] = TLField(flag=1 << 4)
    saved_info: Optional[TLObject] = TLField(flag=1 << 0)
    saved_credentials: Optional[TLObject] = TLField(flag=1 << 1)
    users: list[TLObject] = TLField()
