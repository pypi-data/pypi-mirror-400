from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x673ac2f9, name="functions.payments.GetStarsTransactions_181")
class GetStarsTransactions_181(TLObject):
    flags: Int = TLField(is_flags=True)
    inbound: bool = TLField(flag=1 << 0)
    outbound: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    offset: str = TLField()
