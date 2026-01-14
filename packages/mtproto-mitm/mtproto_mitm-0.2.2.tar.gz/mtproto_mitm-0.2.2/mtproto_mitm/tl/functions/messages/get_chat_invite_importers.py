from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdf04dd4e, name="functions.messages.GetChatInviteImporters")
class GetChatInviteImporters(TLObject):
    flags: Int = TLField(is_flags=True)
    requested: bool = TLField(flag=1 << 0)
    subscription_expired: bool = TLField(flag=1 << 3)
    peer: TLObject = TLField()
    link: Optional[str] = TLField(flag=1 << 1)
    q: Optional[str] = TLField(flag=1 << 2)
    offset_date: Int = TLField()
    offset_user: TLObject = TLField()
    limit: Int = TLField()
