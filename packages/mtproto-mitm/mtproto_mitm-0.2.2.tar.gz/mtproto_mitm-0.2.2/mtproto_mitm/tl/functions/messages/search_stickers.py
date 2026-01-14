from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x29b1c66a, name="functions.messages.SearchStickers")
class SearchStickers(TLObject):
    flags: Int = TLField(is_flags=True)
    emojis: bool = TLField(flag=1 << 0)
    q: str = TLField()
    emoticon: str = TLField()
    lang_code: list[str] = TLField()
    offset: Int = TLField()
    limit: Int = TLField()
    hash: Long = TLField()
