from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x74bbb43d, name="functions.phone.ToggleGroupCallSettings_122")
class ToggleGroupCallSettings_122(TLObject):
    flags: Int = TLField(is_flags=True)
    call: TLObject = TLField()
    join_muted: bool = TLField(flag=1 << 0, flag_serializable=True)
