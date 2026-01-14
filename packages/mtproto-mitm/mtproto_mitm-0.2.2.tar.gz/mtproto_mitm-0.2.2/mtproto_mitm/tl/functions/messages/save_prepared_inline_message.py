from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf21f7f2f, name="functions.messages.SavePreparedInlineMessage")
class SavePreparedInlineMessage(TLObject):
    flags: Int = TLField(is_flags=True)
    result: TLObject = TLField()
    user_id: TLObject = TLField()
    peer_types: Optional[list[TLObject]] = TLField(flag=1 << 0)
