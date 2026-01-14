from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xddf10c3b, name="types.MessageMediaWebPage")
class MessageMediaWebPage(TLObject):
    flags: Int = TLField(is_flags=True)
    force_large_media: bool = TLField(flag=1 << 0)
    force_small_media: bool = TLField(flag=1 << 1)
    manual: bool = TLField(flag=1 << 3)
    safe: bool = TLField(flag=1 << 4)
    webpage: TLObject = TLField()
