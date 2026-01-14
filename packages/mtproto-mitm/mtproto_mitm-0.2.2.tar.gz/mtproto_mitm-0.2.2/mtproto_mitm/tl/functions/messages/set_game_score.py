from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8ef8ecc0, name="functions.messages.SetGameScore")
class SetGameScore(TLObject):
    flags: Int = TLField(is_flags=True)
    edit_message: bool = TLField(flag=1 << 0)
    force: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    id: Int = TLField()
    user_id: TLObject = TLField()
    score: Int = TLField()
