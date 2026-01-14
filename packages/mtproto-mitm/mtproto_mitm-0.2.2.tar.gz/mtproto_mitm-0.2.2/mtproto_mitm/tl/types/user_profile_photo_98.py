from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xecd75d8c, name="types.UserProfilePhoto_98")
class UserProfilePhoto_98(TLObject):
    photo_id: Long = TLField()
    photo_small: TLObject = TLField()
    photo_big: TLObject = TLField()
    dc_id: Int = TLField()
