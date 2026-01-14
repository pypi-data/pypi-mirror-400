from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc7770878, name="functions.payments.ChangeStarsSubscription")
class ChangeStarsSubscription(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    subscription_id: str = TLField()
    canceled: bool = TLField(flag=1 << 0, flag_serializable=True)
