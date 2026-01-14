from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x97d64341, name="types.UpdateGroupCall_196")
class UpdateGroupCall_196(TLObject):
    flags: Int = TLField(is_flags=True)
    chat_id: Optional[Long] = TLField(flag=1 << 0)
    call: TLObject = TLField()
