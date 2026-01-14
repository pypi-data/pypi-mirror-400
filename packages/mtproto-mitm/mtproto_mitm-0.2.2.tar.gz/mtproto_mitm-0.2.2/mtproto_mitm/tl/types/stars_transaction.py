from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x13659eb0, name="types.StarsTransaction")
class StarsTransaction(TLObject):
    flags: Int = TLField(is_flags=True)
    refund: bool = TLField(flag=1 << 3)
    pending: bool = TLField(flag=1 << 4)
    failed: bool = TLField(flag=1 << 6)
    gift: bool = TLField(flag=1 << 10)
    reaction: bool = TLField(flag=1 << 11)
    stargift_upgrade: bool = TLField(flag=1 << 18)
    business_transfer: bool = TLField(flag=1 << 21)
    stargift_resale: bool = TLField(flag=1 << 22)
    posts_search: bool = TLField(flag=1 << 24)
    stargift_prepaid_upgrade: bool = TLField(flag=1 << 25)
    stargift_drop_original_details: bool = TLField(flag=1 << 26)
    phonegroup_message: bool = TLField(flag=1 << 27)
    stargift_auction_bid: bool = TLField(flag=1 << 28)
    offer: bool = TLField(flag=1 << 29)
    id: str = TLField()
    amount: TLObject = TLField()
    date: Int = TLField()
    peer: TLObject = TLField()
    title: Optional[str] = TLField(flag=1 << 0)
    description: Optional[str] = TLField(flag=1 << 1)
    photo: Optional[TLObject] = TLField(flag=1 << 2)
    transaction_date: Optional[Int] = TLField(flag=1 << 5)
    transaction_url: Optional[str] = TLField(flag=1 << 5)
    bot_payload: Optional[bytes] = TLField(flag=1 << 7)
    msg_id: Optional[Int] = TLField(flag=1 << 8)
    extended_media: Optional[list[TLObject]] = TLField(flag=1 << 9)
    subscription_period: Optional[Int] = TLField(flag=1 << 12)
    giveaway_post_id: Optional[Int] = TLField(flag=1 << 13)
    stargift: Optional[TLObject] = TLField(flag=1 << 14)
    floodskip_number: Optional[Int] = TLField(flag=1 << 15)
    starref_commission_permille: Optional[Int] = TLField(flag=1 << 16)
    starref_peer: Optional[TLObject] = TLField(flag=1 << 17)
    starref_amount: Optional[TLObject] = TLField(flag=1 << 17)
    paid_messages: Optional[Int] = TLField(flag=1 << 19)
    premium_gift_months: Optional[Int] = TLField(flag=1 << 20)
    ads_proceeds_from_date: Optional[Int] = TLField(flag=1 << 23)
    ads_proceeds_to_date: Optional[Int] = TLField(flag=1 << 23)
