from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdcbb8260, name="functions.messages.GetHistory_72")
class GetHistory_72(TLObject):
    peer: TLObject = TLField()
    offset_id: Int = TLField()
    offset_date: Int = TLField()
    add_offset: Int = TLField()
    limit: Int = TLField()
    max_id: Int = TLField()
    min_id: Int = TLField()
    hash: Int = TLField()
