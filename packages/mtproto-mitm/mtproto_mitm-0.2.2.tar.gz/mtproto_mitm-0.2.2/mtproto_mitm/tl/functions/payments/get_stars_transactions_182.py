from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x97938d5a, name="functions.payments.GetStarsTransactions_182")
class GetStarsTransactions_182(TLObject):
    flags: Int = TLField(is_flags=True)
    inbound: bool = TLField(flag=1 << 0)
    outbound: bool = TLField(flag=1 << 1)
    ascending: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    offset: str = TLField()
    limit: Int = TLField()
