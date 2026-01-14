from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x63183030, name="functions.messages.TranslateText")
class TranslateText(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: Optional[TLObject] = TLField(flag=1 << 0)
    id: Optional[list[Int]] = TLField(flag=1 << 0)
    text: Optional[list[TLObject]] = TLField(flag=1 << 1)
    to_lang: str = TLField()
