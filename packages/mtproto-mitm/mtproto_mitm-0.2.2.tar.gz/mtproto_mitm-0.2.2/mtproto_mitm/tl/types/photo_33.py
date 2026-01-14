from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcded42fe, name="types.Photo_33")
class Photo_33(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    sizes: list[TLObject] = TLField()
