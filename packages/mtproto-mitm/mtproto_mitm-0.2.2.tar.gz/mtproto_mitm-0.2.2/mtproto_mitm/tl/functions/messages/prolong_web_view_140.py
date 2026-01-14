from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd22ad148, name="functions.messages.ProlongWebView_140")
class ProlongWebView_140(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    peer: TLObject = TLField()
    bot: TLObject = TLField()
    query_id: Long = TLField()
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 0)
