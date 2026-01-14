from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb2cbc1c0, name="functions.phone.DiscardCall")
class DiscardCall(TLObject):
    flags: Int = TLField(is_flags=True)
    video: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    duration: Int = TLField()
    reason: TLObject = TLField()
    connection_id: Long = TLField()
