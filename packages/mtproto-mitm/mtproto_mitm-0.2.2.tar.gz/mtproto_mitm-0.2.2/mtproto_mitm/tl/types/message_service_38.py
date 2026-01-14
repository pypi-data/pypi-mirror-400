from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc06b9607, name="types.MessageService_38")
class MessageService_38(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    from_id: Optional[Int] = TLField(flag=1 << 8)
    to_id: TLObject = TLField()
    date: Int = TLField()
    action: TLObject = TLField()
