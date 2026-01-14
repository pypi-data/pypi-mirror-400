from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfc87a53c, name="functions.messages.RequestWebView_145")
class RequestWebView_145(TLObject):
    flags: Int = TLField(is_flags=True)
    from_bot_menu: bool = TLField(flag=1 << 4)
    silent: bool = TLField(flag=1 << 5)
    peer: TLObject = TLField()
    bot: TLObject = TLField()
    url: Optional[str] = TLField(flag=1 << 1)
    start_param: Optional[str] = TLField(flag=1 << 3)
    theme_params: Optional[TLObject] = TLField(flag=1 << 2)
    platform: str = TLField()
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 0)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
