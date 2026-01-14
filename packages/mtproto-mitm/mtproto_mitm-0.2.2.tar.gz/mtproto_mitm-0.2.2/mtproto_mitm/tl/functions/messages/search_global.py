from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4bc6589a, name="functions.messages.SearchGlobal")
class SearchGlobal(TLObject):
    flags: Int = TLField(is_flags=True)
    broadcasts_only: bool = TLField(flag=1 << 1)
    groups_only: bool = TLField(flag=1 << 2)
    users_only: bool = TLField(flag=1 << 3)
    folder_id: Optional[Int] = TLField(flag=1 << 0)
    q: str = TLField()
    filter: TLObject = TLField()
    min_date: Int = TLField()
    max_date: Int = TLField()
    offset_rate: Int = TLField()
    offset_peer: TLObject = TLField()
    offset_id: Int = TLField()
    limit: Int = TLField()
