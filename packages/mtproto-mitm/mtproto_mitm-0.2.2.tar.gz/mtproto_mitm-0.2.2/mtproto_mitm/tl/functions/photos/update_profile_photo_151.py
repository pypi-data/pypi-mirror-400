from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1c3d5956, name="functions.photos.UpdateProfilePhoto_151")
class UpdateProfilePhoto_151(TLObject):
    flags: Int = TLField(is_flags=True)
    fallback: bool = TLField(flag=1 << 0)
    id: TLObject = TLField()
