from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6b39f4ec, name="types.payments.StarGiftAuctionState")
class StarGiftAuctionState(TLObject):
    gift: TLObject = TLField()
    state: TLObject = TLField()
    user_state: TLObject = TLField()
    timeout: Int = TLField()
    users: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
