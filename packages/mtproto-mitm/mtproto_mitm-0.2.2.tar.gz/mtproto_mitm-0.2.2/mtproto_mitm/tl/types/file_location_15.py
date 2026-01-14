from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x53d69076, name="types.FileLocation_15")
class FileLocation_15(TLObject):
    dc_id: Int = TLField()
    volume_id: Long = TLField()
    local_id: Int = TLField()
    secret: Long = TLField()
