from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf69e113, name="types.UpdateBotInlineSend_46")
class UpdateBotInlineSend_46(TLObject):
    user_id: Int = TLField()
    query: str = TLField()
    id: str = TLField()
