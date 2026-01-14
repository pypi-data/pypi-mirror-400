from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe98e474, name="types.payments.StarGiftAuctionState_218")
class StarGiftAuctionState_218(TLObject):
    gift: TLObject = TLField()
    state: TLObject = TLField()
    user_state: TLObject = TLField()
    timeout: Int = TLField()
    users: list[TLObject] = TLField()
