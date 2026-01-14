from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb08f922a, name="functions.messages.DeleteHistory")
class DeleteHistory(TLObject):
    flags: Int = TLField(is_flags=True)
    just_clear: bool = TLField(flag=1 << 0)
    revoke: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    max_id: Int = TLField()
    min_date: Optional[Int] = TLField(flag=1 << 2)
    max_date: Optional[Int] = TLField(flag=1 << 3)
