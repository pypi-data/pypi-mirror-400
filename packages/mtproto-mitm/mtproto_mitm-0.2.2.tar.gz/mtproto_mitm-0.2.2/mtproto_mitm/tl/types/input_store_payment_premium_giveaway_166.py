from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7c9375e6, name="types.InputStorePaymentPremiumGiveaway_166")
class InputStorePaymentPremiumGiveaway_166(TLObject):
    flags: Int = TLField(is_flags=True)
    only_new_subscribers: bool = TLField(flag=1 << 0)
    boost_peer: TLObject = TLField()
    additional_peers: Optional[list[TLObject]] = TLField(flag=1 << 1)
    countries_iso2: Optional[list[str]] = TLField(flag=1 << 2)
    random_id: Long = TLField()
    until_date: Int = TLField()
    currency: str = TLField()
    amount: Long = TLField()
