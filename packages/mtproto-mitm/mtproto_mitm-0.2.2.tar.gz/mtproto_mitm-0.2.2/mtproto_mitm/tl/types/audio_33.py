from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf9e35055, name="types.Audio_33")
class Audio_33(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    duration: Int = TLField()
    mime_type: str = TLField()
    size: Int = TLField()
    dc_id: Int = TLField()
