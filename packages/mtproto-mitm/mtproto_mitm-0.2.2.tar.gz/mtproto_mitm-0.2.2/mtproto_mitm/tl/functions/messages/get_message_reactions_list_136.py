from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe0ee6b77, name="functions.messages.GetMessageReactionsList_136")
class GetMessageReactionsList_136(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    id: Int = TLField()
    reaction: Optional[str] = TLField(flag=1 << 0)
    offset: Optional[str] = TLField(flag=1 << 1)
    limit: Int = TLField()
