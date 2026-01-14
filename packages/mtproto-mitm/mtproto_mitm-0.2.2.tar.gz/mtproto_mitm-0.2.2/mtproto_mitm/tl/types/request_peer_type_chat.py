from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc9f06e1b, name="types.RequestPeerTypeChat")
class RequestPeerTypeChat(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    bot_participant: bool = TLField(flag=1 << 5)
    has_username: bool = TLField(flag=1 << 3, flag_serializable=True)
    forum: bool = TLField(flag=1 << 4, flag_serializable=True)
    user_admin_rights: Optional[TLObject] = TLField(flag=1 << 1)
    bot_admin_rights: Optional[TLObject] = TLField(flag=1 << 2)
