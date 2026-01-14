from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x14b9bcd7, name="functions.messages.ExportChatInvite_124")
class ExportChatInvite_124(TLObject):
    flags: Int = TLField(is_flags=True)
    legacy_revoke_permanent: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    expire_date: Optional[Int] = TLField(flag=1 << 0)
    usage_limit: Optional[Int] = TLField(flag=1 << 1)
