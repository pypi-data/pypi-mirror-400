from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x15051f54, name="types.photos.PhotosSlice")
class PhotosSlice(TLObject):
    count: Int = TLField()
    photos: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
