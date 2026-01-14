from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2e13f4c3, name="types.User_66")
class User_66(TLObject):
    flags: Int = TLField(is_flags=True)
    is_self: bool = TLField(flag=1 << 10)
    contact: bool = TLField(flag=1 << 11)
    mutual_contact: bool = TLField(flag=1 << 12)
    deleted: bool = TLField(flag=1 << 13)
    bot: bool = TLField(flag=1 << 14)
    bot_chat_history: bool = TLField(flag=1 << 15)
    bot_nochats: bool = TLField(flag=1 << 16)
    verified: bool = TLField(flag=1 << 17)
    restricted: bool = TLField(flag=1 << 18)
    min: bool = TLField(flag=1 << 20)
    bot_inline_geo: bool = TLField(flag=1 << 21)
    id: Int = TLField()
    access_hash: Optional[Long] = TLField(flag=1 << 0)
    first_name: Optional[str] = TLField(flag=1 << 1)
    last_name: Optional[str] = TLField(flag=1 << 2)
    username: Optional[str] = TLField(flag=1 << 3)
    phone: Optional[str] = TLField(flag=1 << 4)
    photo: Optional[TLObject] = TLField(flag=1 << 5)
    status: Optional[TLObject] = TLField(flag=1 << 6)
    bot_info_version: Optional[Int] = TLField(flag=1 << 14)
    restriction_reason: Optional[str] = TLField(flag=1 << 18)
    bot_inline_placeholder: Optional[str] = TLField(flag=1 << 19)
    lang_code: Optional[str] = TLField(flag=1 << 22)
