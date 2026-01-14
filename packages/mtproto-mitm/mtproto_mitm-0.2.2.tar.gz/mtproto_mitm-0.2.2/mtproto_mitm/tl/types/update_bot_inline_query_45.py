from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc01eea08, name="types.UpdateBotInlineQuery_45")
class UpdateBotInlineQuery_45(TLObject):
    query_id: Long = TLField()
    user_id: Int = TLField()
    query: str = TLField()
    offset: str = TLField()
