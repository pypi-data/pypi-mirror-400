from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf47741f7, name="types.PeerSettings")
class PeerSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    report_spam: bool = TLField(flag=1 << 0)
    add_contact: bool = TLField(flag=1 << 1)
    block_contact: bool = TLField(flag=1 << 2)
    share_contact: bool = TLField(flag=1 << 3)
    need_contacts_exception: bool = TLField(flag=1 << 4)
    report_geo: bool = TLField(flag=1 << 5)
    autoarchived: bool = TLField(flag=1 << 7)
    invite_members: bool = TLField(flag=1 << 8)
    request_chat_broadcast: bool = TLField(flag=1 << 10)
    business_bot_paused: bool = TLField(flag=1 << 11)
    business_bot_can_reply: bool = TLField(flag=1 << 12)
    geo_distance: Optional[Int] = TLField(flag=1 << 6)
    request_chat_title: Optional[str] = TLField(flag=1 << 9)
    request_chat_date: Optional[Int] = TLField(flag=1 << 9)
    business_bot_id: Optional[Long] = TLField(flag=1 << 13)
    business_bot_manage_url: Optional[str] = TLField(flag=1 << 13)
    charge_paid_message_stars: Optional[Long] = TLField(flag=1 << 14)
    registration_month: Optional[str] = TLField(flag=1 << 15)
    phone_country: Optional[str] = TLField(flag=1 << 16)
    name_change_date: Optional[Int] = TLField(flag=1 << 17)
    photo_change_date: Optional[Int] = TLField(flag=1 << 18)
