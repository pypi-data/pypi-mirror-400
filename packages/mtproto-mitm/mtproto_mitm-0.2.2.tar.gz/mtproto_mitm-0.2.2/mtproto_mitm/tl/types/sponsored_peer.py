from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc69708d3, name="types.SponsoredPeer")
class SponsoredPeer(TLObject):
    flags: Int = TLField(is_flags=True)
    random_id: bytes = TLField()
    peer: TLObject = TLField()
    sponsor_info: Optional[str] = TLField(flag=1 << 0)
    additional_info: Optional[str] = TLField(flag=1 << 1)
