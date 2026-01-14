from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd2cfdb0e, name="types.MessageActionGiftCode_166")
class MessageActionGiftCode_166(TLObject):
    flags: Int = TLField(is_flags=True)
    via_giveaway: bool = TLField(flag=1 << 0)
    unclaimed: bool = TLField(flag=1 << 2)
    boost_peer: Optional[TLObject] = TLField(flag=1 << 1)
    months: Int = TLField()
    slug: str = TLField()
