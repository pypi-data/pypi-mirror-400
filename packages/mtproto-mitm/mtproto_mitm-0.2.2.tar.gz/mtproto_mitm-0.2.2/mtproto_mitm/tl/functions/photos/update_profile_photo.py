from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9e82039, name="functions.photos.UpdateProfilePhoto")
class UpdateProfilePhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    fallback: bool = TLField(flag=1 << 0)
    bot: Optional[TLObject] = TLField(flag=1 << 1)
    id: TLObject = TLField()
