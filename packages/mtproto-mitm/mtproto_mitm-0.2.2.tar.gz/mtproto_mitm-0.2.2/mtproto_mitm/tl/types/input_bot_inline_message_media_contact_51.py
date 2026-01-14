from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2daf01a7, name="types.InputBotInlineMessageMediaContact_51")
class InputBotInlineMessageMediaContact_51(TLObject):
    flags: Int = TLField(is_flags=True)
    phone_number: str = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
