from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x54f882f1, name="functions.messages.SetInlineGameScore_56")
class SetInlineGameScore_56(TLObject):
    flags: Int = TLField(is_flags=True)
    edit_message: bool = TLField(flag=1 << 0)
    id: TLObject = TLField()
    user_id: TLObject = TLField()
    game_id: Int = TLField()
    score: Int = TLField()
