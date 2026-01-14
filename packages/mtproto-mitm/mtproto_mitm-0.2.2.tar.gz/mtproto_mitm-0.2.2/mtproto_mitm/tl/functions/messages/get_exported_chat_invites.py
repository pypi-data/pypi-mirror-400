from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa2b5a3f6, name="functions.messages.GetExportedChatInvites")
class GetExportedChatInvites(TLObject):
    flags: Int = TLField(is_flags=True)
    revoked: bool = TLField(flag=1 << 3)
    peer: TLObject = TLField()
    admin_id: TLObject = TLField()
    offset_date: Optional[Int] = TLField(flag=1 << 2)
    offset_link: Optional[str] = TLField(flag=1 << 2)
    limit: Int = TLField()
