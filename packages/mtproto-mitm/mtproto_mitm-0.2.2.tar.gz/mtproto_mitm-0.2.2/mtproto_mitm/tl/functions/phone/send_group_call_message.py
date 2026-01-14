from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb1d11410, name="functions.phone.SendGroupCallMessage")
class SendGroupCallMessage(TLObject):
    flags: Int = TLField(is_flags=True)
    call: TLObject = TLField()
    random_id: Long = TLField()
    message: TLObject = TLField()
    allow_paid_stars: Optional[Long] = TLField(flag=1 << 0)
    send_as: Optional[TLObject] = TLField(flag=1 << 1)
