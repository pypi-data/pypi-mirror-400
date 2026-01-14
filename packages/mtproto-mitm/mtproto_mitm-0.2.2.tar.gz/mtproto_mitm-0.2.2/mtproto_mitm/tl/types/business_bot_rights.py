from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa0624cf7, name="types.BusinessBotRights")
class BusinessBotRights(TLObject):
    flags: Int = TLField(is_flags=True)
    reply: bool = TLField(flag=1 << 0)
    read_messages: bool = TLField(flag=1 << 1)
    delete_sent_messages: bool = TLField(flag=1 << 2)
    delete_received_messages: bool = TLField(flag=1 << 3)
    edit_name: bool = TLField(flag=1 << 4)
    edit_bio: bool = TLField(flag=1 << 5)
    edit_profile_photo: bool = TLField(flag=1 << 6)
    edit_username: bool = TLField(flag=1 << 7)
    view_gifts: bool = TLField(flag=1 << 8)
    sell_gifts: bool = TLField(flag=1 << 9)
    change_gift_settings: bool = TLField(flag=1 << 10)
    transfer_and_upgrade_gifts: bool = TLField(flag=1 << 11)
    transfer_stars: bool = TLField(flag=1 << 12)
    manage_stories: bool = TLField(flag=1 << 13)
