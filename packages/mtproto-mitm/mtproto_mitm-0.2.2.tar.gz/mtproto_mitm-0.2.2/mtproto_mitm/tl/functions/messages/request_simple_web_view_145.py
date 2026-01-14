from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x299bec8e, name="functions.messages.RequestSimpleWebView_145")
class RequestSimpleWebView_145(TLObject):
    flags: Int = TLField(is_flags=True)
    bot: TLObject = TLField()
    url: str = TLField()
    theme_params: Optional[TLObject] = TLField(flag=1 << 0)
    platform: str = TLField()
