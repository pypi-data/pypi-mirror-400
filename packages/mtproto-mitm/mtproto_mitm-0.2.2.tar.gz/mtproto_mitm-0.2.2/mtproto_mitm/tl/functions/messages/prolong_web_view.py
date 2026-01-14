from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb0d81a83, name="functions.messages.ProlongWebView")
class ProlongWebView(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    peer: TLObject = TLField()
    bot: TLObject = TLField()
    query_id: Long = TLField()
    reply_to: Optional[TLObject] = TLField(flag=1 << 0)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
