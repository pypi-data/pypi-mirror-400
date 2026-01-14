from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x59ead627, name="functions.phone.SetCallRating")
class SetCallRating(TLObject):
    flags: Int = TLField(is_flags=True)
    user_initiative: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    rating: Int = TLField()
    comment: str = TLField()
