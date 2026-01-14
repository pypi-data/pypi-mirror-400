from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xee9f4a4d, name="types.Video_28")
class Video_28(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    user_id: Int = TLField()
    date: Int = TLField()
    duration: Int = TLField()
    size: Int = TLField()
    thumb: TLObject = TLField()
    dc_id: Int = TLField()
    w: Int = TLField()
    h: Int = TLField()
