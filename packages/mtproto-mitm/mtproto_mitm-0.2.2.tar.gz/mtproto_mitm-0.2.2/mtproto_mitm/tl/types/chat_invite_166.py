from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcde0ec40, name="types.ChatInvite_166")
class ChatInvite_166(TLObject):
    flags: Int = TLField(is_flags=True)
    channel: bool = TLField(flag=1 << 0)
    broadcast: bool = TLField(flag=1 << 1)
    public: bool = TLField(flag=1 << 2)
    megagroup: bool = TLField(flag=1 << 3)
    request_needed: bool = TLField(flag=1 << 6)
    verified: bool = TLField(flag=1 << 7)
    scam: bool = TLField(flag=1 << 8)
    fake: bool = TLField(flag=1 << 9)
    title: str = TLField()
    about: Optional[str] = TLField(flag=1 << 5)
    photo: TLObject = TLField()
    participants_count: Int = TLField()
    participants: Optional[list[TLObject]] = TLField(flag=1 << 4)
    color: Int = TLField()
