from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x770656a8, name="types.InputAppEvent_15")
class InputAppEvent_15(TLObject):
    time: float = TLField()
    type_: str = TLField()
    peer: Long = TLField()
    data: str = TLField()
