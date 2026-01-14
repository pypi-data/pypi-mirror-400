from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x48720fe8, name="types.InputMediaContextBotResult_44")
class InputMediaContextBotResult_44(TLObject):
    flags: Int = TLField(is_flags=True)
    media: bool = TLField(flag=1 << 0)
    bot: TLObject = TLField()
    url: str = TLField()
    query_id: Long = TLField()
