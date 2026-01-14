from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbddcc510, name="types.InputBotInlineMessageMediaWebPage")
class InputBotInlineMessageMediaWebPage(TLObject):
    flags: Int = TLField(is_flags=True)
    invert_media: bool = TLField(flag=1 << 3)
    force_large_media: bool = TLField(flag=1 << 4)
    force_small_media: bool = TLField(flag=1 << 5)
    optional: bool = TLField(flag=1 << 6)
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    url: str = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
