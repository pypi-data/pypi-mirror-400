from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x44e56023, name="types.messages.EmojiGameDiceInfo")
class EmojiGameDiceInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    game_hash: str = TLField()
    prev_stake: Long = TLField()
    current_streak: Int = TLField()
    params: list[Int] = TLField()
    plays_left: Optional[Int] = TLField(flag=1 << 0)
