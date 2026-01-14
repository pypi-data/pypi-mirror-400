from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x21202222, name="functions.messages.GetDialogUnreadMarks")
class GetDialogUnreadMarks(TLObject):
    flags: Int = TLField(is_flags=True)
    parent_peer: Optional[TLObject] = TLField(flag=1 << 0)
