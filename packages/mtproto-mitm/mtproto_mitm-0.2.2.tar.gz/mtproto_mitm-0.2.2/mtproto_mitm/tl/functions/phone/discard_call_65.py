from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x78d413a6, name="functions.phone.DiscardCall_65")
class DiscardCall_65(TLObject):
    peer: TLObject = TLField()
    duration: Int = TLField()
    reason: TLObject = TLField()
    connection_id: Long = TLField()
