from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x36b0816, name="types.PageBlockEmbed_59")
class PageBlockEmbed_59(TLObject):
    url: str = TLField()
    w: Int = TLField()
    h: Int = TLField()
    caption: TLObject = TLField()
