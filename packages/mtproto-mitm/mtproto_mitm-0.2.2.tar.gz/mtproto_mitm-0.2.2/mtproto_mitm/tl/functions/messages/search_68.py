from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf288a275, name="functions.messages.Search_68")
class Search_68(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    q: str = TLField()
    from_id: Optional[TLObject] = TLField(flag=1 << 0)
    filter: TLObject = TLField()
    min_date: Int = TLField()
    max_date: Int = TLField()
    offset: Int = TLField()
    max_id: Int = TLField()
    limit: Int = TLField()
