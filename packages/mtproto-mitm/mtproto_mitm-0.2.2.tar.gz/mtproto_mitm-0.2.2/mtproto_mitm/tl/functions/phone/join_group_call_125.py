from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb132ff7b, name="functions.phone.JoinGroupCall_125")
class JoinGroupCall_125(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    call: TLObject = TLField()
    join_as: TLObject = TLField()
    invite_hash: Optional[str] = TLField(flag=1 << 1)
    params: TLObject = TLField()
