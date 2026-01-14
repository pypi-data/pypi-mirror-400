from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xee430c85, name="types.GroupCallDonor")
class GroupCallDonor(TLObject):
    flags: Int = TLField(is_flags=True)
    top: bool = TLField(flag=1 << 0)
    my: bool = TLField(flag=1 << 1)
    peer_id: Optional[TLObject] = TLField(flag=1 << 3)
    stars: Long = TLField()
