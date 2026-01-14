from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc9e01e7b, name="functions.messages.RequestMainWebView")
class RequestMainWebView(TLObject):
    flags: Int = TLField(is_flags=True)
    compact: bool = TLField(flag=1 << 7)
    fullscreen: bool = TLField(flag=1 << 8)
    peer: TLObject = TLField()
    bot: TLObject = TLField()
    start_param: Optional[str] = TLField(flag=1 << 1)
    theme_params: Optional[TLObject] = TLField(flag=1 << 0)
    platform: str = TLField()
