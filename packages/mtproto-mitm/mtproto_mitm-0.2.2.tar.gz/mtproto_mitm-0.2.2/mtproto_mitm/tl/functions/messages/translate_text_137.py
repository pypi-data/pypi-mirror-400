from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x24ce6dee, name="functions.messages.TranslateText_137")
class TranslateText_137(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: Optional[TLObject] = TLField(flag=1 << 0)
    msg_id: Optional[Int] = TLField(flag=1 << 0)
    text: Optional[str] = TLField(flag=1 << 1)
    from_lang: Optional[str] = TLField(flag=1 << 2)
    to_lang: str = TLField()
