from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1d2652ee, name="functions.account.FinishTakeoutSession")
class FinishTakeoutSession(TLObject):
    flags: Int = TLField(is_flags=True)
    success: bool = TLField(flag=1 << 0)
