from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x87e2f155, name="types.MessageActionGiveawayResults")
class MessageActionGiveawayResults(TLObject):
    flags: Int = TLField(is_flags=True)
    stars: bool = TLField(flag=1 << 0)
    winners_count: Int = TLField()
    unclaimed_count: Int = TLField()
