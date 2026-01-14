from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xea0b7eec, name="types.BotContextResult_44")
class BotContextResult_44(TLObject):
    flags: Int = TLField(is_flags=True)
    hide_url: bool = TLField(flag=1 << 0)
    webpage: TLObject = TLField()
