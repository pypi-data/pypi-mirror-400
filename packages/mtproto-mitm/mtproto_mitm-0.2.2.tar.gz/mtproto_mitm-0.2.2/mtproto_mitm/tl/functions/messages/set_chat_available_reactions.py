from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x864b2581, name="functions.messages.SetChatAvailableReactions")
class SetChatAvailableReactions(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    available_reactions: TLObject = TLField()
    reactions_limit: Optional[Int] = TLField(flag=1 << 0)
    paid_enabled: bool = TLField(flag=1 << 1, flag_serializable=True)
