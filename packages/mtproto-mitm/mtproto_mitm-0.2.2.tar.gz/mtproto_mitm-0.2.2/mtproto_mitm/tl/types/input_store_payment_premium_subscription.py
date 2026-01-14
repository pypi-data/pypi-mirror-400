from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa6751e66, name="types.InputStorePaymentPremiumSubscription")
class InputStorePaymentPremiumSubscription(TLObject):
    flags: Int = TLField(is_flags=True)
    restore: bool = TLField(flag=1 << 0)
    upgrade: bool = TLField(flag=1 << 1)
