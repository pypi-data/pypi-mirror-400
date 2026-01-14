from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa02ce5d5, name="functions.messages.ExportChatInvite_134")
class ExportChatInvite_134(TLObject):
    flags: Int = TLField(is_flags=True)
    legacy_revoke_permanent: bool = TLField(flag=1 << 2)
    request_needed: bool = TLField(flag=1 << 3)
    peer: TLObject = TLField()
    expire_date: Optional[Int] = TLField(flag=1 << 0)
    usage_limit: Optional[Int] = TLField(flag=1 << 1)
    title: Optional[str] = TLField(flag=1 << 4)
