from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x751f08fa, name="types.InputStorePaymentStarsGiveaway")
class InputStorePaymentStarsGiveaway(TLObject):
    flags: Int = TLField(is_flags=True)
    only_new_subscribers: bool = TLField(flag=1 << 0)
    winners_are_visible: bool = TLField(flag=1 << 3)
    stars: Long = TLField()
    boost_peer: TLObject = TLField()
    additional_peers: Optional[list[TLObject]] = TLField(flag=1 << 1)
    countries_iso2: Optional[list[str]] = TLField(flag=1 << 2)
    prize_description: Optional[str] = TLField(flag=1 << 4)
    random_id: Long = TLField()
    until_date: Int = TLField()
    currency: str = TLField()
    amount: Long = TLField()
    users: Int = TLField()
