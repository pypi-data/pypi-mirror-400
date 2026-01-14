from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x91cd32a8, name="functions.photos.GetUserPhotos")
class GetUserPhotos(TLObject):
    user_id: TLObject = TLField()
    offset: Int = TLField()
    max_id: Long = TLField()
    limit: Int = TLField()
