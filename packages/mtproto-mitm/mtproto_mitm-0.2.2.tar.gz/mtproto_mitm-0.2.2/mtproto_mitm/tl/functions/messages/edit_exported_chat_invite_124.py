from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2e4ffbe, name="functions.messages.EditExportedChatInvite_124")
class EditExportedChatInvite_124(TLObject):
    flags: Int = TLField(is_flags=True)
    revoked: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    link: str = TLField()
    expire_date: Optional[Int] = TLField(flag=1 << 0)
    usage_limit: Optional[Int] = TLField(flag=1 << 1)
