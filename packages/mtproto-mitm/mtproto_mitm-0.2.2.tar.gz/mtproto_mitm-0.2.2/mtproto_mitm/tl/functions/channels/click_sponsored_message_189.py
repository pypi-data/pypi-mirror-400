from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1445d75, name="functions.channels.ClickSponsoredMessage_189")
class ClickSponsoredMessage_189(TLObject):
    flags: Int = TLField(is_flags=True)
    media: bool = TLField(flag=1 << 0)
    fullscreen: bool = TLField(flag=1 << 1)
    channel: TLObject = TLField()
    random_id: bytes = TLField()
