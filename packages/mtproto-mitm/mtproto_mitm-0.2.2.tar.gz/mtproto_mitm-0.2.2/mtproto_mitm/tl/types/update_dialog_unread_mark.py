from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb658f23e, name="types.UpdateDialogUnreadMark")
class UpdateDialogUnreadMark(TLObject):
    flags: Int = TLField(is_flags=True)
    unread: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    saved_peer_id: Optional[TLObject] = TLField(flag=1 << 1)
