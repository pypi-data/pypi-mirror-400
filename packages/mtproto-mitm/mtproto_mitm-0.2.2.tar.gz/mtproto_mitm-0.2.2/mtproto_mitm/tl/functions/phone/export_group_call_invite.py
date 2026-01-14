from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe6aa647f, name="functions.phone.ExportGroupCallInvite")
class ExportGroupCallInvite(TLObject):
    flags: Int = TLField(is_flags=True)
    can_self_unmute: bool = TLField(flag=1 << 0)
    call: TLObject = TLField()
