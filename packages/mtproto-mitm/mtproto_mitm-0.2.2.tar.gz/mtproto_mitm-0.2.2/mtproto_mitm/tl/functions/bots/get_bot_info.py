from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdcd914fd, name="functions.bots.GetBotInfo")
class GetBotInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    bot: Optional[TLObject] = TLField(flag=1 << 0)
    lang_code: str = TLField()
