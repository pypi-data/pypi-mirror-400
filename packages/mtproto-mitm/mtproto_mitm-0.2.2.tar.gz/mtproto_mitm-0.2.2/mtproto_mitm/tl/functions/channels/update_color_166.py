from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x621a201f, name="functions.channels.UpdateColor_166")
class UpdateColor_166(TLObject):
    flags: Int = TLField(is_flags=True)
    channel: TLObject = TLField()
    color: Int = TLField()
    background_emoji_id: Optional[Long] = TLField(flag=1 << 0)
