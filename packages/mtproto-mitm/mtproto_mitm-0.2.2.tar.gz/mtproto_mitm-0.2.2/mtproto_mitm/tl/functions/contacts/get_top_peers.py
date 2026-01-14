from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x973478b6, name="functions.contacts.GetTopPeers")
class GetTopPeers(TLObject):
    flags: Int = TLField(is_flags=True)
    correspondents: bool = TLField(flag=1 << 0)
    bots_pm: bool = TLField(flag=1 << 1)
    bots_inline: bool = TLField(flag=1 << 2)
    phone_calls: bool = TLField(flag=1 << 3)
    forward_users: bool = TLField(flag=1 << 4)
    forward_chats: bool = TLField(flag=1 << 5)
    groups: bool = TLField(flag=1 << 10)
    channels: bool = TLField(flag=1 << 15)
    bots_app: bool = TLField(flag=1 << 16)
    offset: Int = TLField()
    limit: Int = TLField()
    hash: Long = TLField()
