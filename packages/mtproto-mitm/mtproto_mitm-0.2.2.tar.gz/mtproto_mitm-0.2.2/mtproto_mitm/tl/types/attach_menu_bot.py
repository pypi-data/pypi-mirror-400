from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd90d8dfe, name="types.AttachMenuBot")
class AttachMenuBot(TLObject):
    flags: Int = TLField(is_flags=True)
    inactive: bool = TLField(flag=1 << 0)
    has_settings: bool = TLField(flag=1 << 1)
    request_write_access: bool = TLField(flag=1 << 2)
    show_in_attach_menu: bool = TLField(flag=1 << 3)
    show_in_side_menu: bool = TLField(flag=1 << 4)
    side_menu_disclaimer_needed: bool = TLField(flag=1 << 5)
    bot_id: Long = TLField()
    short_name: str = TLField()
    peer_types: Optional[list[TLObject]] = TLField(flag=1 << 3)
    icons: list[TLObject] = TLField()
