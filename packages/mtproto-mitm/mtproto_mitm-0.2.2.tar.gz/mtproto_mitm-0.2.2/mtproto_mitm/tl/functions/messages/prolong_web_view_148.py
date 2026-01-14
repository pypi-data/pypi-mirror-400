from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7ff34309, name="functions.messages.ProlongWebView_148")
class ProlongWebView_148(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    peer: TLObject = TLField()
    bot: TLObject = TLField()
    query_id: Long = TLField()
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 0)
    top_msg_id: Optional[Int] = TLField(flag=1 << 9)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
