from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x461b3f48, name="functions.messages.GetMessageReactionsList")
class GetMessageReactionsList(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    id: Int = TLField()
    reaction: Optional[TLObject] = TLField(flag=1 << 0)
    offset: Optional[str] = TLField(flag=1 << 1)
    limit: Int = TLField()
