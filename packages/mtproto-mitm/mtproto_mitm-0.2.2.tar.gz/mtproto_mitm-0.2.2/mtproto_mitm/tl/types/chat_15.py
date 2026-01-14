from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6e9c9bc7, name="types.Chat_15")
class Chat_15(TLObject):
    id: Int = TLField()
    title: str = TLField()
    photo: TLObject = TLField()
    participants_count: Int = TLField()
    date: Int = TLField()
    left: bool = TLField()
    version: Int = TLField()
