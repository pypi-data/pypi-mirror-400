from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5fb224d5, name="types.ChatAdminRights")
class ChatAdminRights(TLObject):
    flags: Int = TLField(is_flags=True)
    change_info: bool = TLField(flag=1 << 0)
    post_messages: bool = TLField(flag=1 << 1)
    edit_messages: bool = TLField(flag=1 << 2)
    delete_messages: bool = TLField(flag=1 << 3)
    ban_users: bool = TLField(flag=1 << 4)
    invite_users: bool = TLField(flag=1 << 5)
    pin_messages: bool = TLField(flag=1 << 7)
    add_admins: bool = TLField(flag=1 << 9)
    anonymous: bool = TLField(flag=1 << 10)
    manage_call: bool = TLField(flag=1 << 11)
    other: bool = TLField(flag=1 << 12)
    manage_topics: bool = TLField(flag=1 << 13)
    post_stories: bool = TLField(flag=1 << 14)
    edit_stories: bool = TLField(flag=1 << 15)
    delete_stories: bool = TLField(flag=1 << 16)
    manage_direct_messages: bool = TLField(flag=1 << 17)
