from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9f120418, name="types.ChatBannedRights")
class ChatBannedRights(TLObject):
    flags: Int = TLField(is_flags=True)
    view_messages: bool = TLField(flag=1 << 0)
    send_messages: bool = TLField(flag=1 << 1)
    send_media: bool = TLField(flag=1 << 2)
    send_stickers: bool = TLField(flag=1 << 3)
    send_gifs: bool = TLField(flag=1 << 4)
    send_games: bool = TLField(flag=1 << 5)
    send_inline: bool = TLField(flag=1 << 6)
    embed_links: bool = TLField(flag=1 << 7)
    send_polls: bool = TLField(flag=1 << 8)
    change_info: bool = TLField(flag=1 << 10)
    invite_users: bool = TLField(flag=1 << 15)
    pin_messages: bool = TLField(flag=1 << 17)
    manage_topics: bool = TLField(flag=1 << 18)
    send_photos: bool = TLField(flag=1 << 19)
    send_videos: bool = TLField(flag=1 << 20)
    send_roundvideos: bool = TLField(flag=1 << 21)
    send_audios: bool = TLField(flag=1 << 22)
    send_voices: bool = TLField(flag=1 << 23)
    send_docs: bool = TLField(flag=1 << 24)
    send_plain: bool = TLField(flag=1 << 25)
    until_date: Int = TLField()
