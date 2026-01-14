from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x58cf4249, name="types.ChannelBannedRights_68")
class ChannelBannedRights_68(TLObject):
    flags: Int = TLField(is_flags=True)
    view_messages: bool = TLField(flag=1 << 0)
    send_messages: bool = TLField(flag=1 << 1)
    send_media: bool = TLField(flag=1 << 2)
    send_stickers: bool = TLField(flag=1 << 3)
    send_gifs: bool = TLField(flag=1 << 4)
    send_games: bool = TLField(flag=1 << 5)
    send_inline: bool = TLField(flag=1 << 6)
    embed_links: bool = TLField(flag=1 << 7)
    until_date: Int = TLField()
